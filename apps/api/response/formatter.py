"""
Response formatter for standardizing API responses.
"""
from typing import Dict, Any, Optional


def success_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format success response.
    
    Args:
        data: Response data
        message: Optional success message
    
    Returns:
        Formatted success response
    """
    response = {
        "success": True
    }
    
    if message:
        response["message"] = message
    
    if data is not None:
        response["data"] = data
    
    return response


    return response


def error_response(
    error: str,
    message: Optional[str] = None,
    code: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    details: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        error: Error type/category (e.g. "validation_error", "unauthorized")
        message: Legacy human-readable message (fallback)
        code: I18n error code (e.g. "AUTH_INVALID_TOKEN")
        params: Parameters for i18n message interpolation
        details: Optional technical details
        data: Optional data payload
    
    Returns:
        Formatted error response
    """
    response = {
        "success": False,
        "error": error
    }
    
    # Priority: Code > Message
    if code:
        response["code"] = code
        
    if params:
        response["params"] = params
        
    # Keep message for backward compatibility or debugging
    if message:
        response["message"] = message
    
    if details:
        response["details"] = details
        
    if data:
        response["data"] = data
    
    return response

