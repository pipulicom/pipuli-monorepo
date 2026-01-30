from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService
from decorators import require_auth
from messages import SuccessMessages, ErrorMessages
from constants import MOVEMENT_ID_PREFIX, TIMESTAMP_MULTIPLIER
from .movement_validator import validate_movement_fields

@require_auth
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Create a new asset movement.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Created movement data
    """
    workflow_logger = logger.for_module("workflow.create_asset_movement")
    uid = data["_uid"]  # Injected by @require_auth decorator
    
    # 2. Extract and Validate Asset ID
    asset_id = data.get("assetId")
    if not asset_id:
        return error_response(
            error="validation_error",
            message=ErrorMessages.ASSET_ID_MISSING
        )
    
    # 3. Verify Asset Exists and Get Type
    try:
        db_service = DatabaseService(config, logger)
        asset_collection = f"users/{uid}/assets"
        asset = db_service.get(collection=asset_collection, document_id=asset_id)
        
        if not asset:
            return error_response(
                error="not_found",
                message=ErrorMessages.ASSET_NOT_FOUND
            )
        
        # Check if asset has been soft-deleted
        if asset.get("deletedAt"):
            return error_response(
                error="forbidden",
                message=ErrorMessages.ASSET_DELETED_CANNOT_ADD_MOVEMENT
            )
        
        asset_type = asset.get("type")
        if asset_type not in ["INVESTMENT", "PROPERTY"]:
            return error_response(
                error="validation_error",
                message=ErrorMessages.INVALID_ASSET_TYPE
            )
        
    except Exception as e:
        workflow_logger.error("Error fetching asset", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.ASSET_NOT_FOUND
        )
    
    # 4. Extract Input Fields
    month = data.get("month")
    contribution = data.get("contribution")
    withdraw = data.get("withdraw")
    current_gross_balance = data.get("currentGrossBalance")
    market_value = data.get("marketValue")
    outstanding_balance = data.get("outstandingBalance")
    
    # 5. Validate using centralized validator
    is_valid, error = validate_movement_fields(
        month=month,
        contribution=contribution,
        withdraw=withdraw,
        asset_type=asset_type,
        current_gross_balance=current_gross_balance,
        market_value=market_value,
        outstanding_balance=outstanding_balance,
        required=True  # All fields required for creation
    )
    if not is_valid:
        return error
    
    # 6. Prepare Movement Data
    movement_data = {
        "assetId": asset_id,
        "month": month.strip(),
        "contribution": float(contribution),
        "withdraw": float(withdraw),
        "assetType": asset_type
    }
    
    # Add type-specific fields
    if asset_type == "INVESTMENT":
        movement_data["currentGrossBalance"] = float(current_gross_balance)
    elif asset_type == "PROPERTY":
        movement_data["marketValue"] = float(market_value)
        movement_data["outstandingBalance"] = float(outstanding_balance)
    
    # 6. Generate Movement ID and Timestamp
    timestamp = int(datetime.now(timezone.utc).timestamp() * TIMESTAMP_MULTIPLIER)
    movement_id = f"{MOVEMENT_ID_PREFIX}{timestamp}"
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    movement_data["id"] = movement_id
    movement_data["createdAt"] = created_at
    
    # 7. Save to Subcollection
    try:
        movements_collection = f"users/{uid}/assets/{asset_id}/movements"
        
        db_service.create(
            collection=movements_collection,
            data=movement_data,
            document_id=movement_id
        )
        
        workflow_logger.info(
            f"Movement created successfully",
            {"movement_id": movement_id, "asset_id": asset_id, "uid": uid}
        )
        

        
        return success_response(
            message=SuccessMessages.MOVEMENT_CREATED,
            data=movement_data
        )
        
    except Exception as e:
        workflow_logger.error("Error saving movement to database", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_SAVE.format(item="movement")
        )
