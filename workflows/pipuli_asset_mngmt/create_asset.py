from typing import Dict, Any
import uuid
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService
from decorators import require_auth
from messages import SuccessMessages, ErrorMessages
from .asset_validator import validate_asset_fields

@require_auth
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Create a new asset.
    
    Args:
        data: Request data (must contain _auth injected by gateway)
        config: Project configuration
        logger: Logger instance
        
    Returns:
        Created asset data
    """
    workflow_logger = logger.for_module("workflow.create_asset")
    uid = data["_uid"]  # Injected by @require_auth decorator
    
    # 2. Extract and Validate Input
    name = data.get("name")
    asset_type = data.get("type", "INVESTMENT") # Default to INVESTMENT
    category = data.get("category")
    tags = data.get("tags", [])
    
    # Validate Input using centralized validator
    is_valid, error = validate_asset_fields(
        name=name,
        asset_type=asset_type,
        category=category,
        required=True  # All fields required for creation
    )
    if not is_valid:
        return error
    
    # 3. Prepare Asset Data
    asset_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    asset_data = {
        "id": asset_id,
        "name": name,
        "type": asset_type,
        "category": category,
        "tags": tags,
        "createdAt": created_at
    }
    
    # 4. Save to Database
    try:
        db_service = DatabaseService(config, logger)
        # Collection: users/{uid}/assets
        collection_path = f"users/{uid}/assets"
        
        db_service.create(
            collection=collection_path,
            data=asset_data,
            document_id=asset_id
        )
        
        workflow_logger.info(f"Asset created successfully", {"asset_id": asset_id, "uid": uid})
        
        return success_response(
            message=SuccessMessages.ASSET_CREATED,
            data=asset_data
        )
        
    except Exception as e:
        workflow_logger.error("Error saving asset to database", error=e)
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_SAVE.format(item="asset")
        )
