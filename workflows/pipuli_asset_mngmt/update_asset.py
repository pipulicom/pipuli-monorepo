from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService
from decorators import require_auth
from messages import SuccessMessages, ErrorMessages
from .asset_validator import validate_asset_fields

@require_auth
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Update an existing asset.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Updated asset data
    """
    workflow_logger = logger.for_module("workflow.update_asset")
    uid = data["_uid"]  # Injected by @require_auth decorator
    
    # 2. Extract Asset ID
    asset_id = data.get("assetId")
    if not asset_id:
        return error_response(
            error="validation_error",
            message=ErrorMessages.ASSET_ID_MISSING
        )
    
    # 3. Extract and Validate Input
    name = data.get("name")
    asset_type = data.get("type")
    category = data.get("category")
    tags = data.get("tags", [])
    
    # Validate Input using centralized validator
    
    is_valid, error = validate_asset_fields(
        name=name,
        asset_type=asset_type,
        category=category,
        required=False  # Only validate provided fields
    )
    if not is_valid:
        return error
    
    # 4. Check if Asset Exists
    try:
        db_service = DatabaseService(config, logger)
        collection_path = f"users/{uid}/assets"
        
        existing_asset = db_service.get(
            collection=collection_path,
            document_id=asset_id
        )
        
        if not existing_asset:
            workflow_logger.warning(f"Asset not found", {"asset_id": asset_id, "uid": uid})
            return error_response(
                error="not_found",
                message=ErrorMessages.ASSET_NOT_FOUND
            )
        
        # Check if asset is soft-deleted
        if existing_asset.get("deletedAt"):
            workflow_logger.warning(f"Attempt to update deleted asset", {"asset_id": asset_id, "uid": uid})
            return error_response(
                error="not_found",
                message=ErrorMessages.ASSET_DELETED
            )
        
    except Exception as e:
        workflow_logger.error("Error checking asset existence", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_GENERIC
        )
    
    # 5. Prepare Update Data
    updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    update_data = {
        "updatedAt": updated_at
    }
    
    # Only update fields that were provided
    if name is not None:
        update_data["name"] = name
    if asset_type is not None:
        update_data["type"] = asset_type
    if category is not None:
        update_data["category"] = category
    if "tags" in data:  # Allow empty tags array
        update_data["tags"] = tags
    
    # 6. Update Asset in Database
    try:
        db_service.update(
            collection=collection_path,
            document_id=asset_id,
            data=update_data
        )
        
        # Get the updated asset
        updated_asset = db_service.get(
            collection=collection_path,
            document_id=asset_id
        )
        
        workflow_logger.info(f"Asset updated successfully", {"asset_id": asset_id, "uid": uid})
        
        return success_response(
            message=SuccessMessages.ASSET_UPDATED,
            data=updated_asset
        )
        
    except Exception as e:
        workflow_logger.error("Error updating asset in database", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_UPDATE.format(item="asset")
        )
