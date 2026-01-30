from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Soft delete a specific movement from an asset.
    
    Args:
        data: Request data (must contain _auth, assetId, and movementId)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Confirmation of movement deletion
    """
    workflow_logger = logger.for_module("workflow.delete_asset_movement")
    
    # 1. Extract Auth Data
    auth_data = data.get("_auth")
    if not auth_data:
        workflow_logger.error("Missing auth data in request")
        return error_response(
            error="unauthorized",
            message="Who goes there? Identify yourself (Missing Token)."
        )
    
    uid = auth_data.get("uid")
    
    # 2. Extract and Validate Input
    asset_id = data.get("assetId")
    movement_id = data.get("movementId")
    
    if not asset_id:
        return error_response(
            error="validation_error",
            message="We need a target. Asset ID is missing."
        )
    
    if not movement_id:
        return error_response(
            error="validation_error",
            message="Which movement? Movement ID is required."
        )
    
    # 3. Verify Asset Exists and Is Not Deleted
    try:
        db_service = DatabaseService(config, logger)
        asset_collection = f"users/{uid}/assets"
        
        asset = db_service.get(collection=asset_collection, document_id=asset_id)
        
        if not asset:
            return error_response(
                error="not_found",
                message="Ghost Asset? We can't find that one in your books."
            )
        
        if asset.get("deletedAt"):
            return error_response(
                error="forbidden",
                message="Cannot rewrite history of a deleted asset."
            )
        
        # 4. Verify Movement Exists and Belongs to This Asset
        movements_collection = f"users/{uid}/assets/{asset_id}/movements"
        
        # Get movement WITHOUT filtering (to check if already deleted)
        movement = db_service.get(
            collection=movements_collection,
            document_id=movement_id
        )
        
        if not movement:
            return error_response(
                error="not_found",
                message="Movement not found. Maybe it never existed?"
            )
        
        # 5. Check if Already Deleted (Idempotency)
        if movement.get("deletedAt"):
            workflow_logger.info(f"Movement {movement_id} already deleted, returning idempotent response")
            return success_response(
                message="Movement erased from history.",
                data={
                    "assetId": asset_id,
                    "movementId": movement_id,
                    "deletedAt": movement.get("deletedAt")
                }
            )
        
        workflow_logger.info(
            f"Soft deleting movement: {movement_id}",
            {"uid": uid, "asset_id": asset_id}
        )
        
        # 6. Soft Delete the Movement
        deleted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        db_service.update(
            collection=movements_collection,
            document_id=movement_id,
            data={"deletedAt": deleted_at}
        )
        

        
        # 8. Return Success Response
        workflow_logger.info(
            f"Movement soft deleted successfully",
            {"movement_id": movement_id, "asset_id": asset_id}
        )
        
        return success_response(
            message="Movement erased from history.",
            data={
                "assetId": asset_id,
                "movementId": movement_id,
                "deletedAt": deleted_at
            }
        )
        
    except Exception as e:
        workflow_logger.error("Error soft deleting movement", error=e)
        return error_response(
            error="database_error",
            message="Time travel failed. Couldn't erase that movement."
        )
