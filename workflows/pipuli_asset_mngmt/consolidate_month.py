from typing import Dict, Any, List
from logger.logger import Logger
from services.database import DatabaseService

def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Consolidate monthly summary for a user.
    
    Args:
        data: {
            "uid": str,
            "month": str (YYYY-MM)
        }
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Consolidated summary data
    """
    workflow_logger = logger.for_module("workflow.consolidate_month")
    
    uid = data.get("uid")
    month = data.get("month")
    
    if not uid or not month:
        workflow_logger.error("Missing uid or month for consolidation")
        return {"error": "Missing required parameters"}
        
    workflow_logger.info(f"Starting consolidation for user {uid}, month {month}")
    
    db_service = DatabaseService(config, logger)
    
    # Initialize totals
    stats = {
        "netWorth": 0.0,
        "totalAssets": 0.0,
        "totalLiabilities": 0.0,
        "flowIn": 0.0,
        "flowOut": 0.0,
        "netFlow": 0.0
    }
    
    breakdown = {
        "INVESTMENT": 0.0,
        "PROPERTY": 0.0
    }
    
    try:
        # 1. Get all assets
        assets_collection = f"users/{uid}/assets"
        assets = db_service.list(
            collection=assets_collection,
            limit=100,
            exclude_deleted=True  # Filter soft-deleted assets
        )
        
        for asset in assets:
            asset_id = asset.get("id")
            asset_type = asset.get("type", "INVESTMENT")
            movements_collection = f"users/{uid}/assets/{asset_id}/movements"
            
            # 2. Get movements for the target month (for Flow and potentially Balance)
            current_month_movements = db_service.query(
                collection=movements_collection,
                filters=[("month", "==", month)],
                exclude_deleted=True  # Filter soft-deleted movements
            )
            
            latest_movement = None
            
            if current_month_movements:
                # Calculate Flow from ALL movements in this month
                for mov in current_month_movements:
                    stats["flowIn"] += float(mov.get("contribution", 0))
                    stats["flowOut"] += float(mov.get("withdraw", 0))
                
                # Find latest movement for Balance
                # Sort by createdAt descending
                current_month_movements.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
                latest_movement = current_month_movements[0]
                
            else:
                # No movements in target month, look for previous month (Carry Over)
                # Find the last month with activity
                previous_months = db_service.query(
                    collection=movements_collection,
                    filters=[("month", "<", month)],
                    order_by="month",
                    descending=True,
                    limit=1,
                    exclude_deleted=True  # Filter soft-deleted movements
                )
                
                if previous_months:
                    last_active_month = previous_months[0].get("month")
                    # Get movements from that month to find the latest one
                    last_month_movements = db_service.query(
                        collection=movements_collection,
                        filters=[("month", "==", last_active_month)],
                        exclude_deleted=True  # Filter soft-deleted movements
                    )
                    if last_month_movements:
                        last_month_movements.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
                        latest_movement = last_month_movements[0]
            
            # 3. Add to Net Worth / Totals if we have a state
            if latest_movement:
                if asset_type == "INVESTMENT":
                    balance = float(latest_movement.get("currentGrossBalance", 0))
                    stats["totalAssets"] += balance
                    breakdown["INVESTMENT"] += balance
                
                elif asset_type == "PROPERTY":
                    market_value = float(latest_movement.get("marketValue", 0))
                    outstanding = float(latest_movement.get("outstandingBalance", 0))
                    
                    stats["totalAssets"] += market_value
                    stats["totalLiabilities"] += outstanding
                    breakdown["PROPERTY"] += (market_value - outstanding) # Equity
        
        # Final calculations
        stats["netWorth"] = stats["totalAssets"] - stats["totalLiabilities"]
        stats["netFlow"] = stats["flowIn"] - stats["flowOut"]
        
        # 4. Save Summary
        from datetime import datetime, timezone
        updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        summary_data = {
            "month": month,
            "stats": stats,
            "breakdownByCategory": breakdown,
            "updatedAt": updated_at
        }
        
        # Use set to overwrite/create
        summary_collection = f"users/{uid}/monthly_summaries"
        db_service.create(
            collection=summary_collection,
            data=summary_data,
            document_id=month
        )
        
        workflow_logger.info(f"Consolidation complete for {month}", {"stats": stats})
        return summary_data
        
    except Exception as e:
        workflow_logger.error("Error during consolidation", error=e)
        raise e
