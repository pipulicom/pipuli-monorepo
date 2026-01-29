
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

from services.database import DatabaseService

# Configuration
TARGET_UID = "xRefNorQ75fZMD0CSm4yIJj0FIl2"
PROJECT_ID = "pipuli-asset-mngmt-8cbf4"

def main():
    config = {
        "project_id": PROJECT_ID,
        "credentials_path": "configs/credentials/pipuli-asset-mngmt-firebase.json",
        "database": {"database_id": "(default)"}
    }
    
    try:
        db = DatabaseService(config)
        print(f"Checking assets for user: {TARGET_UID}")
        
        assets = db.list(f"users/{TARGET_UID}/assets")
        print(f"Total Assets Found: {len(assets)}")
        
        for asset in assets:
            print(f"- {asset.get('name')} ({asset.get('type')}) - {asset.get('category')}")
            # Check movements
            movements = db.list(f"users/{TARGET_UID}/assets/{asset['id']}/movements", limit=5)
            print(f"  > Movements: {len(movements)} (showing first few...)")
            
    except Exception as e:
        print(f"Error verification: {e}")

if __name__ == "__main__":
    main()
