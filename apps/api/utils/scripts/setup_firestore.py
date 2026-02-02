#!/usr/bin/env python3
"""
Firestore Setup Script.

Initializes collections for a specific environment (dev/prod) to ensure
connectivity and structure.

Usage:
    ENV=dev python apps/api/utils/scripts/setup_firestore.py
    ENV=prod python apps/api/utils/scripts/setup_firestore.py
"""
import sys
import os
from pathlib import Path

# Add project root to python path
# Script is at: apps/api/utils/scripts/setup_firestore.py
# Root is 4 levels up
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.append(project_root)
# Also add apps/api to path so internal imports work
sys.path.append(os.path.join(project_root, "apps", "api"))

from apps.api.configs.loader import load_config
from apps.api.services.database import DatabaseService
from apps.api.utils.logger import Logger

def setup_firestore():
    env = os.getenv("ENV", "dev")
    print(f"🔧 Setting up Firestore for environment: {env.upper()}")
    
    # Load config
    # We pass a dummy project_id because loader requires it, 
    # but infrastructure config comes from ENV.
    config = load_config("setup-script")
    
    gcp_project = config.get("gcp_project_id")
    print(f"   GCP Project ID: {gcp_project}")
    
    if "your-" in gcp_project:
        print("❌ Error: Please update 'gcp_project_id' in configs/dev.json or configs/prod.json")
        return

    logger = Logger("setup-script", "setup")
    db = DatabaseService(config, logger)
    
    collections = ["assets", "movements", "summaries"]
    
    print("\n   Checking/Initializing collections:")
    for col in collections:
        try:
            # check if collection has docs
            docs = db.list(col, limit=1)
            if docs:
                print(f"   ✅ Collection '{col}' already exists ({len(docs)}+ docs)")
            else:
                print(f"   ⚠️ Collection '{col}' is empty.")
                # Optional: Create a placeholder doc?
                # db.create(col, {"_init": True, "exclude": True}, "init_doc")
                # print(f"      Created init document in '{col}'")
        except Exception as e:
            print(f"   ❌ Error accessing '{col}': {e}")
            print("      (Make sure you have authenticated with 'gcloud auth application-default login')")

    print(f"\n✅ Setup check complete for {env.upper()}")

if __name__ == "__main__":
    setup_firestore()
