from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService
from decorators import require_auth
from messages import SuccessMessages, ErrorMessages
from .movement_validator import validate_movement_fields

@require_auth
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Update an existing asset movement.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Updated movement data
    """
    workflow_logger = logger.for_module("workflow.update_asset_movement")
    uid = data["_uid"]  # Injected by @require_auth decorator
    
    # 2. Extract and Validate IDs
    asset_id = data.get("assetId")
    if not asset_id:
        return error_response(
            error="validation_error",
            message=ErrorMessages.ASSET_ID_MISSING
        )
    
    movement_id = data.get("movementId")
    if not movement_id:
        return error_response(
            error="validation_error",
            message=ErrorMessages.MOVEMENT_ID_MISSING
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
                message=ErrorMessages.ASSET_DELETED_CANNOT_UPDATE_MOVEMENT
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
    
    # 4. Verify Movement Exists
    try:
        movements_collection = f"users/{uid}/assets/{asset_id}/movements"
        existing_movement = db_service.get(
            collection=movements_collection,
            document_id=movement_id
        )
        
        if not existing_movement:
            workflow_logger.warning(f"Movement not found", {"movement_id": movement_id, "asset_id": asset_id, "uid": uid})
            return error_response(
                error="not_found",
                message=ErrorMessages.MOVEMENT_NOT_FOUND
            )
        
        # Check if movement is soft-deleted
        if existing_movement.get("deletedAt"):
            workflow_logger.warning(f"Attempt to update deleted movement", {"movement_id": movement_id, "asset_id": asset_id, "uid": uid})
            return error_response(
                error="not_found",
                message=ErrorMessages.MOVEMENT_DELETED
            )
        
    except Exception as e:
        workflow_logger.error("Error checking movement existence", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_GENERIC
        )
    
    # 5. Extract and Validate Input
    month = data.get("month")
    contribution = data.get("contribution")
    withdraw = data.get("withdraw")
    current_gross_balance = data.get("currentGrossBalance")
    market_value = data.get("marketValue")
    outstanding_balance = data.get("outstandingBalance")
    
    # Validate using centralized validator
    is_valid, error = validate_movement_fields(
        month=month,
        contribution=contribution,
        withdraw=withdraw,
        asset_type=asset_type,
        current_gross_balance=current_gross_balance,
        market_value=market_value,
        outstanding_balance=outstanding_balance,
        required=False  # Only validate provided fields
    )
    if not is_valid:
        return error
    
    # 6. Prepare Update Data
    updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    update_data = {
        "updatedAt": updated_at
    }
    
    # Only update fields that were provided
    if month is not None:
        update_data["month"] = month.strip()
    if contribution is not None:
        update_data["contribution"] = float(contribution)
    if withdraw is not None:
        update_data["withdraw"] = float(withdraw)
    
    # Type-specific fields
    if asset_type == "INVESTMENT":
        if current_gross_balance is not None:
            update_data["currentGrossBalance"] = float(current_gross_balance)
    elif asset_type == "PROPERTY":
        if market_value is not None:
            update_data["marketValue"] = float(market_value)
        if outstanding_balance is not None:
            update_data["outstandingBalance"] = float(outstanding_balance)
    
    # 7. Update Movement in Database
    try:
        db_service.update(
            collection=movements_collection,
            document_id=movement_id,
            data=update_data
        )
        
        # Get the updated movement
        updated_movement = db_service.get(
            collection=movements_collection,
            document_id=movement_id
        )
        
        workflow_logger.info(f"Movement updated successfully", {"movement_id": movement_id, "asset_id": asset_id, "uid": uid})
        
        # 8. Trigger Monthly Consolidation
        try:
            from workflows.pipuli_asset_mngmt import consolidate_month
            # Use the month from updated movement (in case it was changed)
            consolidation_month = updated_movement.get("month")
            if consolidation_month:
                consolidate_month.execute(
                    data={"uid": uid, "month": consolidation_month},
                    config=config,
                    logger=logger
                )
        except Exception as e:
            # Don't fail the request if consolidation fails, just log it
            workflow_logger.error("Error triggering monthly consolidation", error=e)
        
        return success_response(
            message=SuccessMessages.MOVEMENT_UPDATED,
            data=updated_movement
        )
        
    except Exception as e:
        workflow_logger.error("Error updating movement in database", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_UPDATE.format(item="movement")
        )
