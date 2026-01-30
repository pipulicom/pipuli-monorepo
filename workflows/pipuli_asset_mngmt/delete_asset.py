from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Soft delete an asset and all its movements.
    
    Args:
        data: Request data (must contain _auth injected by gateway and assetId)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Confirmation of deletion with details
    """
    workflow_logger = logger.for_module("workflow.delete_asset")
    
    # 1. Extract Auth Data
    auth_data = data.get("_auth")
    if not auth_data:
        workflow_logger.error("Missing auth data in request")
        return error_response(
            error="unauthorized",
            message="Who goes there? Identify yourself (Missing Token)."
        )
    
    uid = auth_data.get("uid")
    
    # 2. Extract and Validate Asset ID
    asset_id = data.get("assetId")
    if not asset_id:
        return error_response(
            error="validation_error",
            message="We need a target. Asset ID is missing."
        )
    
    # 3. Verify Asset Exists and Belongs to User
    try:
        db_service = DatabaseService(config, logger)
        asset_collection = f"users/{uid}/assets"
        
        # Get asset WITHOUT filtering deleted (to check if it exists)
        asset = db_service.get(collection=asset_collection, document_id=asset_id)
        
        if not asset:
            return error_response(
                error="not_found",
                message="That asset? Never heard of it. (Not found)"
            )
        
        # 4. Check if Already Deleted (Idempotency)
        if asset.get("deletedAt"):
            workflow_logger.info(f"Asset {asset_id} already deleted, returning idempotent response")
            # Calculate movements count (for response consistency)
            movements_collection = f"users/{uid}/assets/{asset_id}/movements"
            try:
                movements = db_service.list(
                    collection=movements_collection,
                    limit=1000,
                    exclude_deleted=False  # Count all movements
                )
                movements_deleted_count = sum(1 for m in movements if m.get("deletedAt"))
            except:
                movements_deleted_count = 0
            
            return success_response(
                message="Asset incinerated. Wiped from the ledger.",
                data={
                    "assetId": asset_id,
                    "assetName": asset.get("name"),
                    "deletedAt": asset.get("deletedAt"),
                    "movementsDeleted": movements_deleted_count
                }
            )
        
        workflow_logger.info(f"Soft deleting asset: {asset_id}", {"uid": uid, "asset_name": asset.get("name")})
        
        # 5. Soft Delete All Movements
        movements_collection = f"users/{uid}/assets/{asset_id}/movements"
        movements_deleted_count = 0
        
        try:
            # Get all movements (active ones)
            movements = db_service.list(
                collection=movements_collection,
                limit=1000,
                exclude_deleted=True
            )
            
            deleted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            # Soft delete each movement
            for movement in movements:
                movement_id = movement.get("id")
                db_service.update(
                    collection=movements_collection,
                    document_id=movement_id,
                    data={"deletedAt": deleted_at}
                )
                movements_deleted_count += 1
            
            workflow_logger.info(f"Soft deleted {movements_deleted_count} movements for asset {asset_id}")
            
        except Exception as e:
            workflow_logger.warning(
                f"Error soft deleting movements for asset {asset_id}",
                error=e
            )
            # Continue with asset deletion even if movements fail
        
        # 6. Soft Delete the Asset
        db_service.update(
            collection=asset_collection,
            document_id=asset_id,
            data={"deletedAt": deleted_at}
        )
        

        
        # 8. Return Success Response
        workflow_logger.info(
            f"Asset soft deleted successfully",
            {
                "asset_id": asset_id,
                "movements_deleted": movements_deleted_count
            }
        )
        
        return success_response(
            message="Asset incinerated. Wiped from the ledger.",
            data={
                "assetId": asset_id,
                "assetName": asset.get("name"),
                "deletedAt": deleted_at,
                "movementsDeleted": movements_deleted_count
            }
        )
        
    except Exception as e:
        workflow_logger.error("Error soft deleting asset", error=e)
        return error_response(
            error="database_error",
            message="The demolition crew failed. Try again."
        )
