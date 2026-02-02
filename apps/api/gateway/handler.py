"""
Request handler for routing to workflows.
"""
import importlib
import os
from typing import Dict, Any, Optional
from utils.logger import Logger
from configs.loader import load_config
from response.formatter import error_response


async def handle_request(
    project_id: str,
    flow_name: str,
    body: Dict[str, Any],
    logger: Optional[Logger] = None
) -> Dict[str, Any]:
    """
    Handle incoming request and route to appropriate workflow.
    
    Args:
        project_id: Project identifier
        flow_name: Workflow name to execute
        body: Request body data
        logger: Logger instance for logging
    
    Returns:
        Response from workflow execution
    """
    handler_logger = logger.for_module("handler") if logger else None
    
    if handler_logger:
        handler_logger.info(f"Handling request for workflow '{flow_name}' in project '{project_id}'")
    
    try:
        # Load project configuration
        if handler_logger:
            handler_logger.info("Loading project configuration")
        config = load_config(project_id)

        
        if handler_logger:
            handler_logger.info("Configuration loaded", {"config_keys": list(config.keys())})
        
        # Try to load workflow
        # Format: workflows/{project_id}/{flow_name}.py or workflows/example/{flow_name}.py
        # Sanitize project_id for python import (replace - with _)
        safe_project_id = project_id.replace("-", "_")
        # Sanitize flow_name for python import (replace - with _)
        safe_flow_name = flow_name.replace("-", "_")
        
        workflow_paths = [
            f"workflows.{safe_project_id}.{safe_flow_name}",
            f"workflows.{safe_flow_name}"
        ]
        
        workflow_module = None
        for path in workflow_paths:
            try:
                if handler_logger:
                    handler_logger.debug(f"Trying to load workflow from: {path}")
                workflow_module = importlib.import_module(path)
                if handler_logger:
                    handler_logger.info(f"Workflow loaded successfully", {"path": path})
                break
            except ImportError:
                continue
        
        if not workflow_module:
            if handler_logger:
                handler_logger.warning(f"Workflow not found: {flow_name}", {"tried_paths": workflow_paths})
            return error_response(
                error="workflow_not_found",
                message=f"Workflow '{flow_name}' not found for project '{project_id}'"
            )
        
        # Check if execute function exists
        if not hasattr(workflow_module, "execute"):
            if handler_logger:
                handler_logger.error(f"Workflow module missing execute function", {"module": workflow_paths})
            return error_response(
                error="workflow_invalid",
                message=f"Workflow '{flow_name}' is missing execute function"
            )
        
        # Execute workflow
        if handler_logger:
            handler_logger.info("Executing workflow", {"flow_name": flow_name, "project_id": project_id})
        
        execute_func = workflow_module.execute
        response = execute_func(body.get("data", body), config, logger)
        
        if handler_logger:
            handler_logger.info("Workflow executed successfully", {"flow_name": flow_name})
        
        return response
        
    except Exception as e:
        if handler_logger:
            handler_logger.error("Error handling request", error=e, data={"flow_name": flow_name, "project_id": project_id})
        return error_response(
            error="handler_error",
            message=f"Error processing request: {str(e)}"
        )

