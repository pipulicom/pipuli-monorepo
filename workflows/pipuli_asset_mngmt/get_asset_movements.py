from typing import Dict, Any
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Retrieve all movements for a specific asset.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        List of asset movements
    """
    workflow_logger = logger.for_module("workflow.get_asset_movements")
    
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
        asset = db_service.get(collection=asset_collection, document_id=asset_id)
        
        if not asset:
            return error_response(
                error="not_found",
                message="Ghost Asset? We can't find that one in your books."
            )
        
        # Check if asset has been soft-deleted
        if asset.get("deletedAt"):
            return error_response(
                error="not_found",
                message="This asset has been incinerated. It no longer exists."
            )
        
        workflow_logger.info(f"Fetching movements for asset: {asset_id}")
        
    except Exception as e:
        workflow_logger.error("Error fetching asset", error=e)
        return error_response(
            error="database_error",
            message="Ghost Asset? We can't find that one in your books."
        )
    
    # 4. Fetch Movements from Subcollection
    try:
        movements_collection = f"users/{uid}/assets/{asset_id}/movements"
        limit = data.get("limit", 100)
        
        movements = db_service.list(
            collection=movements_collection,
            limit=limit,
            exclude_deleted=True  # Filter soft-deleted movements
        )
        
        # Sort by month descending (most recent first)
        movements.sort(key=lambda x: x.get("month", ""), reverse=True)
        
        workflow_logger.info(
            f"Retrieved {len(movements)} movements for asset {asset_id}",
            {"asset_id": asset_id, "count": len(movements)}
        )
        
        return success_response(
            message="History retrieved. Review your conquests.",
            data=movements
        )
        
    except Exception as e:
        workflow_logger.error("Error fetching movements from database", error=e)
        return error_response(
            error="database_error",
            message="The archives are dusty. Couldn't fetch movements. Blow on the cartridge and try again."
        )
