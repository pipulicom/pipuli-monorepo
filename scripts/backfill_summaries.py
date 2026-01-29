
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

from logger.logger import Logger
from services.database import DatabaseService
from workflows.pipuli_asset_mngmt import consolidate_month

# Configuration
TARGET_UID = "9V9MdJCfbHZCeHzwGwJaxkwGnsB2" # User with manual entries
PROJECT_ID = "pipuli-asset-mngmt-8cbf4"
FLOW_NAME = "backfill_summaries_script"

def main():
    logger = Logger(PROJECT_ID, FLOW_NAME)
    script_logger = logger.for_module("script")
    
    config = {
        "project_id": PROJECT_ID,
        "credentials_path": "configs/credentials/pipuli-asset-mngmt-firebase.json",
        "database": {"database_id": "(default)"},
        "auth_project_id": PROJECT_ID
    }
    
    print(f"Starting backfill for user: {TARGET_UID}")
    
    try:
        db_service = DatabaseService(config, logger)
        
        # 1. Identify all months with activity
        # We need to scan all movements.
        
        # Get all assets
        assets = db_service.list(f"users/{TARGET_UID}/assets", limit=100)
        print(f"Found {len(assets)} assets.")
        
        active_months = set()
        
        for asset in assets:
            asset_id = asset["id"]
            movements = db_service.list(f"users/{TARGET_UID}/assets/{asset_id}/movements", limit=100)
            
            for mov in movements:
                if "month" in mov:
                    active_months.add(mov["month"])
        
        sorted_months = sorted(list(active_months))
        print(f"Found activity in {len(sorted_months)} months: {sorted_months}")
        
        # 2. Trigger Consolidation for each month
        for month in sorted_months:
            print(f"Consolidating {month}...")
            try:
                result = consolidate_month.execute(
                    data={"uid": TARGET_UID, "month": month},
                    config=config,
                    logger=logger
                )
                if "error" not in result:
                    print(f"  > Success: NetWorth {result['stats']['netWorth']}")
                else:
                    print(f"  > Failed: {result['error']}")
            except Exception as e:
                print(f"  > Error: {e}")
                
        print("Backfill complete.")
        logger.save()
        
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()
