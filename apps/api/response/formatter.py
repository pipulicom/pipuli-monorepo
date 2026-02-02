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


def error_response(
    error: str,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        error: Error type or code
        message: Error message
        details: Optional error details
        data: Optional data payload (alias for details or additional data)
    
    Returns:
        Formatted error response
    """
    response = {
        "success": False,
        "error": error
    }
    
    if message:
        response["message"] = message
    
    if details:
        response["details"] = details
        
    if data:
        response["data"] = data
    
    return response

