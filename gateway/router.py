"""
Gateway router for handling API requests.
"""
from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional, Dict, Any
from gateway.validator import validate_api_key
from gateway.handler import handle_request
from logger.logger import Logger
from services.auth import AuthService
from response.formatter import error_response as format_error_response

router = APIRouter()


@router.api_route("/{project_id}/{flow_name}", methods=["GET", "POST"])
async def process_request(
    project_id: str,
    flow_name: str,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """
    Main endpoint for processing API requests.
    
    Args:
        project_id: Project identifier
        flow_name: Workflow name to execute
        request: FastAPI request object
        x_api_key: API key from header
        authorization: Bearer token for user authentication
    
    Returns:
        Response from workflow execution
    """
    # Initialize logger
    logger = Logger(project_id, flow_name)
    gateway_logger = logger.for_module("gateway")
    
    gateway_logger.info("Request received", {
        "project_id": project_id,
        "flow_name": flow_name,
        "method": request.method,
        "path": str(request.url.path)
    })
    
    # Get request body (if any)
    body = {}
    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}
            
    # Merge Query Parameters into body
    # This allows GET requests to pass data to workflows
    query_params = dict(request.query_params)
    if query_params:
        body.update(query_params)
        gateway_logger.info("Merged query parameters into body", {"params": list(query_params.keys())})
    
    # Get headers as dict
    headers_dict = {key: value for key, value in request.headers.items()}
    
    # Save request
    logger.save_request(
        method=request.method,
        path=str(request.url.path),
        headers=headers_dict,
        body=body,
        client_ip=request.client.host if request.client else None
    )
    
    # Validate API key
    if not x_api_key:
        gateway_logger.warning("API key missing")
        error_response = format_error_response(
            error="unauthorized",
            message="API key is required. Provide X-API-Key header."
        )
        logger.save_response(401, error_response)
        logger.save()
        raise HTTPException(status_code=401, detail=error_response.get("message"))
    
    try:
        # Validate API key via Secret Manager
        gateway_logger.info("Validating API key")
        validate_api_key(x_api_key)
        gateway_logger.info("API key validated successfully")
    except ValueError as e:
        gateway_logger.error("API key validation failed", error=e)
        error_response = format_error_response(
            error="unauthorized",
            message=str(e)
        )
        logger.save_response(401, error_response)
        logger.save()
        raise HTTPException(status_code=401, detail=error_response.get("message"))
    
    # Handle request (route to workflow)
    try:
        # Load config first to check for auth requirements
        from configs.loader import load_config
        config = load_config(project_id)
        config["project_id"] = project_id
        
        # Validate User Token (if auth_project_id is configured)
        if config.get("auth_project_id"):
            gateway_logger.info("Project requires user authentication")
            
            if not authorization or not authorization.startswith("Bearer "):
                gateway_logger.warning("Missing or invalid Authorization header")
                # We might want to allow public endpoints? For now, enforce if configured.
                # Or maybe just pass None if not provided? 
                # User asked for secure flow, so let's enforce if header is present OR if we decide to.
                # For now, let's try to validate if present, or error if missing?
                # Let's enforce it.
                error_response = format_error_response(
                    error="unauthorized",
                    message="Authorization header required (Bearer token)"
                )
                logger.save_response(401, error_response)
                logger.save()
                raise HTTPException(status_code=401, detail=error_response.get("message"))
            
            token = authorization.split(" ")[1]
            auth_service = AuthService(config, logger)
            try:
                user_claims = auth_service.validate_token(token)
                # Inject user info into body data
                target_dict = body
                if "data" in body and isinstance(body["data"], dict):
                    target_dict = body["data"]
                
                target_dict["_auth"] = {
                    "uid": user_claims.get("uid"),
                    "email": user_claims.get("email"),
                    "claims": user_claims
                }
            except ValueError as e:
                gateway_logger.error("Token validation failed", error=e)
                error_response = format_error_response(
                    error="unauthorized",
                    message=str(e)
                )
                logger.save_response(401, error_response)
                logger.save()
                raise HTTPException(status_code=401, detail=error_response.get("message"))

        gateway_logger.info("Routing to handler")
        # We pass the modified body with injected auth data
        response = await handle_request(project_id, flow_name, body, logger)
        
        # Ensure response is standardized
        if not isinstance(response, dict) or "success" not in response:
            gateway_logger.warning("Response not standardized, standardizing")
            response = format_error_response(
                error="internal_error",
                message="Response format error"
            )
        
        gateway_logger.info("Request processed successfully")
        logger.save_response(200, response)
        logger.save()
        return response
    except HTTPException:
        raise
    except Exception as e:
        gateway_logger.error("Error processing request", error=e)
        error_response = format_error_response(
            error="internal_error",
            message=f"Error processing request: {str(e)}"
        )
        logger.save_response(500, error_response)
        logger.save()
        raise HTTPException(
            status_code=500,
            detail=error_response.get("message")
        )

