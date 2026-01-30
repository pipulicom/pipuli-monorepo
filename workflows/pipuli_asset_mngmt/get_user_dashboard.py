from typing import Dict, Any, List
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Retrieve dashboard data with assets and their nested movements.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Dashboard data with assets and movements
    """
    workflow_logger = logger.for_module("workflow.get_user_dashboard")
    
    # 1. Extract Auth Data
    auth_data = data.get("_auth")
    if not auth_data:
        workflow_logger.error("Missing auth data in request")
        return error_response(
            error="unauthorized",
            message="Who goes there? Identify yourself (Missing Token)."
        )
    
    uid = auth_data.get("uid")
    workflow_logger.info(f"Fetching dashboard data for user: {uid}")
    
    # 2. Fetch Assets from Database

    # 2. Fetch Assets from Database
    try:
        db_service = DatabaseService(config, logger)
        assets_collection = f"users/{uid}/assets"
        
        all_assets = db_service.list(
            collection=assets_collection,
            limit=100,
            exclude_deleted=True  # Filter soft-deleted assets
        )
        
        # --- FILTERING LOGIC ---
        filters = {
            "category": data.get("category"),
            "tag": data.get("tag"),
            "assetId": data.get("assetId"),
            "name": data.get("name"),
            "type": data.get("type")
        }
        
        # Remove None values
        active_filters = {k: v for k, v in filters.items() if v is not None}
        
        filtered_assets = []
        for asset in all_assets:
            match = True
            if active_filters.get("assetId") and asset.get("id") != active_filters["assetId"]:
                match = False
            if active_filters.get("category") and asset.get("category") != active_filters["category"]:
                match = False
            if active_filters.get("type") and asset.get("type") != active_filters["type"]:
                match = False
            if active_filters.get("tag"):
                asset_tags = asset.get("tags", [])
                if active_filters["tag"] not in asset_tags:
                    match = False
            if active_filters.get("name"):
                if active_filters["name"].lower() not in asset.get("name", "").lower():
                    match = False
            
            if match:
                filtered_assets.append(asset)
        
        workflow_logger.info(f"Assets after filtering: {len(filtered_assets)} (Total: {len(all_assets)})")
        
        # 3. For Each Filtered Asset, Fetch Its Movements
        assets_with_movements = []
        
        for asset in filtered_assets:
            asset_id = asset.get("id")
            
            try:
                # Fetch movements for this asset
                movements_collection = f"users/{uid}/assets/{asset_id}/movements"
                movements = db_service.list(
                    collection=movements_collection,
                    limit=100,
                    exclude_deleted=True  # Filter soft-deleted movements
                )
                
                # Sort movements by month descending (most recent first)
                movements.sort(key=lambda x: x.get("month", ""), reverse=True)
                
                # Add movements array to asset
                asset["movements"] = movements
                
            except Exception as e:
                workflow_logger.warning(
                    f"Error fetching movements for asset {asset_id}, setting empty array",
                    error=e
                )
                asset["movements"] = []
            
            assets_with_movements.append(asset)
        
        # 4. Return Dashboard Data
        dashboard_data = {
            "assets": assets_with_movements
        }
        
        # 5. Determine Summary Source (Cache vs On-the-Fly)
        # 5. Determine Summary Source (Cache vs On-the-Fly)
        # Summary concept removed
        dashboard_data["summaries"] = []

        workflow_logger.info(
            f"Dashboard data prepared successfully",
            {"assets_count": len(assets_with_movements)}
        )
        
        return success_response(
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        workflow_logger.error("Error fetching dashboard data", error=e)
        return error_response(
            error="database_error",
            message="Radar jammed. Can't see your empire right now. Retrying..."
        )
