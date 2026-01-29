"""
Template canônico de workflow baseado em create_asset.py

Copie este arquivo e adapte conforme necessário.
"""
from typing import Dict, Any
from datetime import datetime, timezone
from logger.logger import Logger
from response.formatter import success_response, error_response
from services.database import DatabaseService
from decorators import require_auth
from messages import SuccessMessages, ErrorMessages
from constants import COLLECTION_NAME  # Adicione sua constant
from .resource_validator import validate_resource_fields  # Crie seu validator

@require_auth
def execute(data: Dict[str, Any], config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    [Brief description of what this workflow does]
    
    Args:
        data: Request data containing:
            - field1 (str): Description of field1
            - field2 (int): Description of field2
            - _uid (str): User ID (injected by @require_auth)
        config: Project configuration
        logger: Logger instance
    
    Returns:
        Dict containing:
            - success (bool): Operation result
            - message (str): Human-readable message
            - data (dict): Resource data if successful
    
    Example:
        >>> data = {
        ...     "_auth": {"uid": "user123"},
        ...     "field1": "value1",
        ...     "field2": 42
        ... }
        >>> result = execute(data, config, logger)
        >>> print(result["success"])
        True
    """
    workflow_logger = logger.for_module("workflow.resource_name")
    uid = data["_uid"]  # Injected by @require_auth decorator
    
    # 1. Extract Input
    field1 = data.get("field1")
    field2 = data.get("field2")
    
    # 2. Validate Input
    is_valid, error = validate_resource_fields(
        field1=field1,
        field2=field2,
        required=True  # True for create, False for update
    )
    if not is_valid:
        return error
    
    # 3. Business Logic
    try:
        db = DatabaseService(config, logger)
        
        # Prepare resource data
        resource_data = {
            "field1": field1,
            "field2": field2,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "deletedAt": None  # Always initialize for soft-delete
        }
        
        # Create in database
        collection_path = f"users/{uid}/resources"
        result = db.create(collection_path, resource_data)
        
        # Log success with context
        workflow_logger.info(
            "Resource created successfully",
            {"resource_id": result["id"], "uid": uid, "field1": field1}
        )
        
        # Return success response
        return success_response(
            message=SuccessMessages.RESOURCE_CREATED,
            data=result
        )
        
    except Exception as e:
        # Log error with context
        workflow_logger.error("Error creating resource", error=e)
        
        # Return error response
        return error_response(
            error="database_error",
            message=ErrorMessages.DB_ERROR_SAVE.format(item="resource")
        )
