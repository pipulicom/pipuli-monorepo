"""
Decorators for common workflow functionality.
"""
from functools import wraps
from typing import Dict, Any, Callable
from response.formatter import error_response
from utils.messages import ErrorMessages


def require_auth(func: Callable) -> Callable:
    """
    Decorator to validate authentication before workflow execution.
    
    Validates that:
    - _auth data exists in request
    - uid exists and is a valid string
    
    Injects validated uid into data as _uid for convenience.
    
    Args:
        func: Workflow execute function to wrap
    
    Returns:
        Wrapped function with auth validation
    
    Example:
        @require_auth
        def execute(data, config, logger):
            uid = data["_uid"]  # Already validated
            ...
    """
    @wraps(func)
    def wrapper(data: Dict[str, Any], config: Dict[str, Any], logger):
        # Validate auth data exists
        auth_data = data.get("_auth")
        if not auth_data:
            logger.for_module("auth").error("Missing auth data in request")
            return error_response(
                error="unauthorized",
                message=ErrorMessages.UNAUTHORIZED
            )
        
        # Validate and extract uid
        uid = auth_data.get("uid")
        if not uid or not isinstance(uid, str):
            logger.for_module("auth").error("Invalid UID in auth data")
            return error_response(
                error="unauthorized",
                message=ErrorMessages.INVALID_UID
            )
        
        # Inject uid into data for convenience
        data["_uid"] = uid
        
        # Execute wrapped function
        return func(data, config, logger)
    
    return wrapper
