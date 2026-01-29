"""
Configuration loader for projects.
"""
import json
import os
from typing import Dict, Any
from google.cloud import secretmanager


def get_secret(secret_name: str, project_id: str = None) -> str:
    """
    Get secret value from Secret Manager.
    
    Args:
        secret_name: Name of the secret
        project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env)
    
    Returns:
        Secret value as string
    """
    if not project_id:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "stan-baas")
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8").strip()
    except Exception:
        # If secret doesn't exist, return empty string
        return ""


def resolve_secrets(config: Dict[str, Any], project_id: str = None):
    """
    Resolve secret references in configuration.
    Replaces api_key_secret references with actual values from Secret Manager.
    
    Args:
        config: Configuration dictionary (modified in place)
        project_id: Google Cloud project ID
    """
    if isinstance(config, dict):
        # Create list of keys to avoid modification during iteration
        keys_to_process = list(config.keys())
        
        for key in keys_to_process:
            value = config[key]
            if key == "api_key_secret" and isinstance(value, str):
                # Replace secret name with actual secret value
                config["api_key"] = get_secret(value, project_id)
                # Remove the secret name reference
                config.pop("api_key_secret", None)
            elif isinstance(value, dict):
                # Recursively resolve secrets in nested dictionaries
                resolve_secrets(value, project_id)
            elif isinstance(value, list):
                # Handle lists (though unlikely in configs)
                for item in value:
                    if isinstance(item, dict):
                        resolve_secrets(item, project_id)


def load_config(project_id: str) -> Dict[str, Any]:
    """
    Load project configuration from JSON file.
    
    Args:
        project_id: Project identifier
    
    Returns:
        Project configuration dictionary
    
    Steps:
        1. Try to load project-specific config: configs/{project_id}.json
        2. If not found, load default: configs/default.json
        3. Resolve secrets from Secret Manager
        4. Add project_id to config
    """
    # Get base directory (where configs folder is)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to load project-specific config
    config_path = os.path.join(base_dir, f"{project_id}.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Load default config
        default_path = os.path.join(base_dir, "default.json")
        if os.path.exists(default_path):
            with open(default_path, 'r') as f:
                config = json.load(f)
        else:
            # Fallback to minimal default if no default.json exists
            config = {
                "database": {
                    "collection_prefix": project_id
                }
            }
    
    # Ensure project_id is set (if not in config)
    if "project_id" not in config:
        config["project_id"] = project_id
    
    # Resolve secrets from Secret Manager
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT", "stan-baas")
    resolve_secrets(config, gcp_project)
    
    return config
