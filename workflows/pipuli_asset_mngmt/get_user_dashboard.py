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
        if not active_filters:
            # NO FILTERS: Fetch pre-calculated summaries
            try:
                summaries_collection = f"users/{uid}/monthly_summaries"
                summaries = db_service.query(
                    collection=summaries_collection,
                    order_by="month",
                    descending=True,
                    limit=12
                )
                dashboard_data["summaries"] = summaries
                workflow_logger.info(f"Retrieved {len(summaries)} monthly summaries from cache")
            except Exception as e:
                workflow_logger.warning("Error fetching monthly summaries", error=e)
                dashboard_data["summaries"] = []
        else:
            # WITH FILTERS: Calculate on-the-fly
            workflow_logger.info("Calculating summaries on-the-fly due to filters")
            
            # Generate list of last 12 months
            from datetime import datetime, timedelta
            today = datetime.now()
            months_to_calc = []
            for i in range(12):
                d = today - timedelta(days=30 * i) # Approx
                months_to_calc.append(d.strftime("%Y-%m"))
            
            calculated_summaries = []
            
            for month in months_to_calc:
                stats = {
                    "netWorth": 0.0,
                    "totalAssets": 0.0,
                    "totalLiabilities": 0.0,
                    "flowIn": 0.0,
                    "flowOut": 0.0,
                    "netFlow": 0.0
                }
                breakdown = {"INVESTMENT": 0.0, "PROPERTY": 0.0}
                
                has_data = False
                
                for asset in assets_with_movements:
                    asset_type = asset.get("type", "INVESTMENT")
                    movements = asset.get("movements", [])
                    
                    # Flow: Exact match for this month
                    month_movements = [m for m in movements if m.get("month") == month]
                    for m in month_movements:
                        stats["flowIn"] += float(m.get("contribution", 0))
                        stats["flowOut"] += float(m.get("withdraw", 0))
                        has_data = True
                        
                    # Balance: Latest movement <= month
                    # Movements are already sorted desc by month. 
                    # We need to find the first one where mov.month <= target_month
                    latest_mov = None
                    for m in movements:
                        if m.get("month") <= month:
                            latest_mov = m
                            break
                    
                    if latest_mov:
                        has_data = True
                        if asset_type == "INVESTMENT":
                            val = float(latest_mov.get("currentGrossBalance", 0))
                            stats["totalAssets"] += val
                            breakdown["INVESTMENT"] += val
                        elif asset_type == "PROPERTY":
                            mkt = float(latest_mov.get("marketValue", 0))
                            out = float(latest_mov.get("outstandingBalance", 0))
                            stats["totalAssets"] += mkt
                            stats["totalLiabilities"] += out
                            breakdown["PROPERTY"] += (mkt - out)
                
                if has_data:
                    stats["netWorth"] = stats["totalAssets"] - stats["totalLiabilities"]
                    stats["netFlow"] = stats["flowIn"] - stats["flowOut"]
                    
                    # Check if we should exclude this month (Current Month Logic)
                    # If it's the current month, and Flow is 0, and NO asset was created, skip it.
                    is_current_month = (month == today.strftime("%Y-%m"))
                    
                    # Use a small tolerance for float comparison
                    is_zero_flow = abs(stats["flowIn"]) < 0.01 and abs(stats["flowOut"]) < 0.01
                    
                    if is_current_month:
                        workflow_logger.info(f"Checking exclusion for current month {month}. FlowIn: {stats['flowIn']}, FlowOut: {stats['flowOut']}")
                    
                    if is_current_month and is_zero_flow:
                        workflow_logger.info(f"Current month {month} has zero flow. Excluding from summary.")
                        continue

                    calculated_summaries.append({
                        "month": month,
                        "stats": stats,
                        "breakdownByCategory": breakdown,
                        "generatedAt": "on-the-fly"
                    })
            
            dashboard_data["summaries"] = calculated_summaries
        
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
