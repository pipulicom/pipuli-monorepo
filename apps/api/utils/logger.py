"""
Logger module for Cloud Logging integration.
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import logging as cloud_logging
import os


class ModuleLogger:
    """
    Wrapper logger that automatically adds module name to all logs.
    """
    
    def __init__(self, logger: 'Logger', module: str):
        """
        Initialize module logger.
        
        Args:
            logger: Base logger instance
            module: Module name
        """
        self.logger = logger
        self.module = module
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log info message with module."""
        self.logger.info(message, data=data, module=self.module)
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None):
        """Log error message with module."""
        self.logger.error(message, error=error, data=data, module=self.module)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message with module."""
        self.logger.warning(message, data=data, module=self.module)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug message with module."""
        self.logger.debug(message, data=data, module=self.module)


class Logger:
    """
    Logger for tracking request/response and workflow logs.
    """
    
    def __init__(
        self,
        project_id: str,
        flow_name: str,
        execution_id: Optional[str] = None
    ):
        """
        Initialize logger.
        
        Args:
            project_id: Project identifier
            flow_name: Workflow name
            execution_id: Optional execution ID (generated if not provided)
        """
        self.project_id = project_id
        self.flow_name = flow_name
        self.execution_id = execution_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.log_entries = []
        
        # Initialize Cloud Logging client
        self.client = cloud_logging.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "pipuli-api"))
        self.service_name = os.getenv("SERVICE_NAME", "pipuli-api")
        self.logger = self.client.logger(self.service_name)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None, module: Optional[str] = None):
        """
        Log info message.
        
        Args:
            message: Log message
            data: Optional additional data
            module: Optional module name
        """
        self._add_log("INFO", message, data, module)
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None, module: Optional[str] = None):
        """
        Log error message.
        
        Args:
            message: Log message
            error: Optional exception
            data: Optional additional data
            module: Optional module name
        """
        error_data = data or {}
        if error:
            error_data["error"] = str(error)
            error_data["error_type"] = type(error).__name__
        self._add_log("ERROR", message, error_data, module)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None, module: Optional[str] = None):
        """
        Log warning message.
        
        Args:
            message: Log message
            data: Optional additional data
            module: Optional module name
        """
        self._add_log("WARNING", message, data, module)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None, module: Optional[str] = None):
        """
        Log debug message.
        
        Args:
            message: Log message
            data: Optional additional data
            module: Optional module name
        """
        self._add_log("DEBUG", message, data, module)
    
    def for_module(self, module: str):
        """
        Return a logger wrapper for a specific module.
        
        Args:
            module: Module name (e.g., "gateway", "handler", "workflow", "service")
        
        Returns:
            ModuleLogger instance
        """
        return ModuleLogger(self, module)
    
    def _add_log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None, module: Optional[str] = None):
        """
        Add log entry.
        
        Args:
            level: Log level
            message: Log message
            data: Optional additional data
            module: Optional module name
        """
        log_entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if module:
            log_entry["module"] = module
        if data:
            log_entry["data"] = data
        
        self.log_entries.append(log_entry)
    
    def save_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
        client_ip: Optional[str] = None
    ):
        """
        Save request information.
        
        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            client_ip: Client IP address
        """
        self.request_data = {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body,
            "client_ip": client_ip,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def save_response(
        self,
        status_code: int,
        body: Dict[str, Any]
    ):
        """
        Save response information.
        
        Args:
            status_code: HTTP status code
            body: Response body
        """
        self.response_data = {
            "status_code": status_code,
            "body": body,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def save(self):
        """
        Save all logs to Cloud Logging.
        """
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        log_data = {
            "project_id": self.project_id,
            "flow_name": self.flow_name,
            "execution_id": self.execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms,
            "logs": self.log_entries
        }
        
        # Add request data if available
        if hasattr(self, 'request_data'):
            log_data["request"] = self.request_data
        
        # Add response data if available
        if hasattr(self, 'response_data'):
            log_data["response"] = self.response_data
        
        # Log to Cloud Logging with structured data for filtering
        self.logger.log_struct(
            log_data,
            severity="INFO",
            labels={
                "project_id": self.project_id,
                "flow_name": self.flow_name,
                "execution_id": self.execution_id
            }
        )

