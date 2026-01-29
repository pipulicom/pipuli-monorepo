"""
Base service class for reusable modules.
"""
from typing import Dict, Any, Optional
from logger.logger import Logger


class BaseService:
    """
    Base class for all services.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        Initialize service.
        
        Args:
            config: Service configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.service_logger = logger.for_module("service") if logger else None
    
    def _log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None):
        """
        Log message if logger is available.
        
        Args:
            level: Log level
            message: Log message
            data: Optional data
            error: Optional exception
        """
        if not self.service_logger:
            return
        
        if level == "info":
            self.service_logger.info(message, data)
        elif level == "error":
            self.service_logger.error(message, error=error, data=data)
        elif level == "warning":
            self.service_logger.warning(message, data)
        elif level == "debug":
            self.service_logger.debug(message, data)

