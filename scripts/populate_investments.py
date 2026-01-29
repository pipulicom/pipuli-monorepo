
import random
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

from logger.logger import Logger
from workflows.pipuli_asset_mngmt import create_asset, create_asset_movement
from services.database import DatabaseService

# Configuration
TARGET_UID = "xRefNorQ75fZMD0CSm4yIJj0FIl2"
PROJECT_ID = "pipuli-asset-mngmt-8cbf4"
FLOW_NAME = "populate_investments_script"

def check_db_connection(config, logger):
    print("Checking database connection...")
    try:
        db = DatabaseService(config, logger)
        # Try a lightweight operation
        db.db.collection("users").limit(1).get()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"CRITICAL: Database connection failed: {e}")
        return False

# Generators
def generate_assets():
    assets = []
    
    # Stocks (Tech/Growth) - 10
    tech_stocks = ["Alpha Tech", "Beta Systems", "Gamma Cyber", "Delta Data", "Epsilon AI", "Zeta Cloud", "Eta Networks", "Theta Robotics", "Iota Quantum", "Kappa Dynamics"]
    for name in tech_stocks:
        assets.append({
            "name": name,
            "category": "Stocks",
            "type": "INVESTMENT",
            "tags": ["tech", "growth", "us-market", "equity"],
            "volatility": "growth" # Mean 0.8%, StdDev 4%
        })

    # ETFs (Global/Sector) - 8
    etfs = ["World Index", "Green Energy ETF", "S&P 500 Tracker", "Emerging Markets", "Dividend Kings", "Tech Sector ETF", "Health Care Fund", "Commodities Basket"]
    for name in etfs:
        assets.append({
            "name": name,
            "category": "ETF",
            "type": "INVESTMENT",
            "tags": ["safe", "diversified", "global", "etf"],
            "volatility": "growth"
        })

    # Crypto (High Volatility) - 5
    cryptos = ["Bitcoin", "Ethereum", "Solana", "Ripple", "Cardano"]
    for name in cryptos:
        assets.append({
            "name": name,
            "category": "Crypto",
            "type": "INVESTMENT",
            "tags": ["crypto", "volatile", "high-risk", "digital-asset"],
            "volatility": "volatile" # Mean 1.5%, StdDev 10%
        })

    # Bonds (Fixed Income) - 5
    bonds = ["US Treasury 10Y", "Corp Bond Apple", "Muni Bond NY", "High Yield Corp", "Gov Bond 2030"]
    for name in bonds:
        assets.append({
            "name": name,
            "category": "Bond",
            "type": "INVESTMENT",
            "tags": ["safe", "yield", "fixed-income", "government"],
            "volatility": "stable" # Mean 0.2%, StdDev 1%
        })

    # Real Estate - 5
    properties = ["Downtown Apartment", "Beach House", "Mountain Cabin", "Suburban Rental", "Commercial Unit"]
    for name in properties:
        assets.append({
            "name": name,
            "category": "Real Estate",
            "type": "PROPERTY",
            "tags": ["property", "illiquid", "real-estate", "hard-asset"],
            "volatility": "property" # Appreciates slowly
        })
        
    # Post-process tags (randomly add long-term)
    for asset in assets:
        if random.random() > 0.5:
            asset["tags"].append("long-term")
            
    return assets

def get_volatility_params(profile):
    if profile == "stable":
        return 0.002, 0.01
    elif profile == "growth":
        return 0.008, 0.04
    elif profile == "volatile":
        return 0.015, 0.10
    elif profile == "property":
        return 0.003, 0.005
    return 0.005, 0.02 # default

def main():
    logger = Logger(PROJECT_ID, FLOW_NAME)
    script_logger = logger.for_module("script")
    
    # Config matching pipuli-asset-mngmt.json
    config = {
        "project_id": PROJECT_ID,
        "credentials_path": "configs/credentials/pipuli-asset-mngmt-firebase.json",
        "database": {"database_id": "(default)"},
        "auth_project_id": PROJECT_ID
    }
    
    print("Starting investment population script...")
    script_logger.info("Starting investment population script")

    # DB Health Check
    if not check_db_connection(config, logger):
        print("Aborting script due to database connection failure.")
        return
    
    assets = generate_assets()
    print(f"Generated {len(assets)} asset definitions")
    
    created_count = 0
    movement_count = 0
    
    for i, asset_def in enumerate(assets):
        # Create Asset - Payload must match decorator expectations
        payload = {
            "_auth": {
                "uid": TARGET_UID,
                "email": "test@example.com"
            },
            "name": asset_def["name"],
            "type": asset_def["type"],
            "category": asset_def["category"],
            "tags": asset_def["tags"]
        }
        
        # Determine initial balance
        if asset_def["type"] == "PROPERTY":
            current_balance = random.randint(200000, 1000000)
            initial_balance = current_balance
        else:
            if "high-risk" in asset_def["tags"]:
                 current_balance = 1000.0
            else:
                 current_balance = 10000.0
            initial_balance = current_balance

        print(f"[{i+1}/{len(assets)}] Creating asset: {asset_def['name']}")
        
        # Execute Workflow
        try:
            result = create_asset.execute(payload, config, logger)
            
            if "error" in result:
                print(f"  FAILED: {result['message']}")
                script_logger.error(f"Failed to create asset: {result['error']}")
                continue
                
            asset_id = result["data"]["id"]
            created_count += 1
            
            # Generate History (24 months)
            # Use fixed start date for consistency: 2023-01 to 2024-12
            start_date = datetime(2023, 1, 1)
            
            for j in range(24):
                month_date = start_date + timedelta(days=j*31) # Approx
                # Reset to 1st of month
                month_date = month_date.replace(day=1)
                month_str = month_date.strftime("%Y-%m")
                
                # Logic
                contribution = 0
                if asset_def["type"] == "INVESTMENT":
                    mean, std = get_volatility_params(asset_def["volatility"])
                    market_move = random.gauss(mean, std)
                    
                    if "growth" in asset_def["volatility"]:
                        contribution = 500
                    elif "volatile" in asset_def["volatility"]:
                         contribution = 100
                    
                    current_balance = (current_balance + contribution) * (1 + market_move)
                    
                    movement_payload = {
                        "_auth": {"uid": TARGET_UID},
                        "assetId": asset_id,
                        "month": month_str,
                        "contribution": contribution,
                        "withdraw": 0,
                        "currentGrossBalance": round(current_balance, 2),
                        "assetType": "INVESTMENT"
                    }
                else: # PROPERTY
                    # Appreciation
                    mean, std = get_volatility_params("property")
                    appreciation = random.gauss(mean, std)
                    current_balance = current_balance * (1 + appreciation)
                    
                    movement_payload = {
                        "_auth": {"uid": TARGET_UID},
                        "assetId": asset_id,
                        "month": month_str,
                        "contribution": 0,
                        "withdraw": 0,
                        "marketValue": round(current_balance, 2),
                        "outstandingBalance": round(initial_balance * 0.8 * (0.99**j), 2),
                        "assetType": "PROPERTY"
                    }

                # Execute Movement Workflow
                try:
                    move_res = create_asset_movement.execute(movement_payload, config, logger)
                    if "success" in move_res:
                         movement_count += 1
                    else:
                         # Ignore "already exists" errors if re-running
                         script_logger.warning(f"Failed movement {month_str}: {move_res.get('message')}")
                except Exception as e:
                    script_logger.error(f"Error creating movement", error=e)
                    
        except Exception as e:
             script_logger.error(f"Error processing asset workflow", error=e)
             print(f"  ERROR: {e}")

    print(f"Completed! Created {created_count} assets and {movement_count} movements.")
    logger.save()

if __name__ == "__main__":
    main()
