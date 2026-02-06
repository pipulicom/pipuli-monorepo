from typing import Any, Dict, Optional

class AppException(Exception):
    """
    Base exception for application logic errors.
    """
    def __init__(
        self, 
        error_type: str, 
        code: str, 
        status_code: int = 400, 
        message: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_type = error_type
        self.code = code
        self.status_code = status_code
        self.message = message
        self.params = params or {}
        self.details = details
        super().__init__(self.message or self.code)
