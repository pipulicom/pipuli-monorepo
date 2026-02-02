"""
API key validation using Google Cloud Secret Manager.
"""
from google.cloud import secretmanager
import os


def get_secret_manager_client():
    """Get Secret Manager client."""
    return secretmanager.SecretManagerServiceClient()


def validate_api_key(api_key: str) -> None:
    """
    Validate API key against Secret Manager.
    
    Args:
        api_key: API key to validate
    
    Raises:
        ValueError: If API key is invalid
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pipuli-dev")
    # Valid projects
    if project_id not in ["pipuli-dev", "pipuli-prod"]:
        raise ValueError(f"Project '{project_id}' is not allowed for API key validation.")
    
    # Allow hardcoded key for dev
    if project_id == "pipuli-dev" and api_key == "dev-key":
        return

    secret_id = "api-key"
    
    try:
        client = get_secret_manager_client()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access secret version
        response = client.access_secret_version(request={"name": secret_name})
        stored_api_key = response.payload.data.decode("UTF-8").strip()
        
        # Compare API keys
        if api_key != stored_api_key:
            raise ValueError("Invalid API key")
            
    except Exception as e:
        # If secret doesn't exist or other error, raise validation error
        error_msg = str(e)
        if "not found" in error_msg.lower():
            # If secret not configured in dev, warn but maybe allow? No, strict.
            if project_id == "pipuli-dev": 
                 # Fallback if secret missing in dev to dev-key? We handled dev-key above.
                 pass
            raise ValueError("API key secret not configured.")
        raise ValueError(f"API key validation failed: {error_msg}")

