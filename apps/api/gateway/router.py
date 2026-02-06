"""
Gateway router for handling API requests.
"""
from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional, Dict, Any
from google.cloud import secretmanager
from gateway.handler import handle_request
from utils.logger import Logger
from services.auth import AuthService
from response.formatter import error_response as format_error_response
import os

router = APIRouter()


def validate_api_key(api_key: str) -> None:
    """
    Validate API key against Secret Manager.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pipuli-dev")
    
    # STRICT MODE: All environments must use Secret Manager
    if project_id not in ["pipuli-dev", "pipuli-prod"]:
        raise ValueError(f"Project '{project_id}' is not allowed for API key validation.")

    secret_id = "api-key"
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access secret version
        response = client.access_secret_version(request={"name": secret_name})
        stored_api_key = response.payload.data.decode("UTF-8").strip()
        
        # Compare API keys
        if api_key != stored_api_key:
            raise ValueError("Invalid API key")
            
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
             pass # Fallback handled by raising error below
        raise ValueError("API key validation failed")


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

    # Inject Method into body for workflows to use
    body["_method"] = request.method
    
    # Save request
    logger.save_request(
        method=request.method,
        path=str(request.url.path),
        headers=headers_dict,
        body=body,
        client_ip=request.client.host if request.client else None
    )
    
from utils.exceptions import AppException

# ... (inside process_request)

    # Validate API key
    if not x_api_key:
        gateway_logger.warning("API key missing")
        error_response = format_error_response(
            error="unauthorized",
            code="AUTH_API_KEY_REQUIRED",
            message="API key is required. Provide X-API-Key header."
        )
        logger.save_response(401, error_response)
        logger.save()
        raise AppException(
            error_type="unauthorized",
            code="AUTH_API_KEY_REQUIRED",
            status_code=401,
            message="API key is required."
        )
    
    try:
        # Validate API key via Secret Manager
        gateway_logger.info("Validating API key")
        validate_api_key(x_api_key)
        gateway_logger.info("API key validated successfully")
    except ValueError as e:
        gateway_logger.error("API key validation failed", error=e)
        error_response = format_error_response(
            error="unauthorized",
            code="AUTH_INVALID_API_KEY",
            message=str(e)
        )
        logger.save_response(401, error_response)
        logger.save()
        raise AppException(
            error_type="unauthorized",
            code="AUTH_INVALID_API_KEY",
            status_code=401,
            message=str(e)
        )
    
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
                error_response = format_error_response(
                    error="unauthorized",
                    code="AUTH_TOKEN_REQUIRED",
                    message="Authorization header required (Bearer token)"
                )
                logger.save_response(401, error_response)
                logger.save()
                raise AppException(
                    error_type="unauthorized",
                    code="AUTH_TOKEN_REQUIRED",
                    status_code=401,
                    message="Authorization header required."
                )
            
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
                    code="AUTH_INVALID_TOKEN",
                    message=str(e)
                )
                logger.save_response(401, error_response)
                logger.save()
                raise AppException(
                    error_type="unauthorized",
                    code="AUTH_INVALID_TOKEN",
                    status_code=401,
                    message=str(e)
                )

        gateway_logger.info("Routing to handler")
        # We pass the modified body with injected auth data
        response = await handle_request(project_id, flow_name, body, logger)
        
        # Ensure response is standardized
        if not isinstance(response, dict) or "success" not in response:
            gateway_logger.warning("Response not standardized, standardizing")
            response = format_error_response(
                error="internal_error",
                code="INTERNAL_RESPONSE_FORMAT_ERROR",
                message="Response format error"
            )
        
        gateway_logger.info("Request processed successfully")
        logger.save_response(200, response)
        logger.save()
        return response

    except AppException:
        # Re-raise AppException to be handled by the global handler
        raise
    except Exception as e:
        gateway_logger.error("Error processing request", error=e)
        error_response = format_error_response(
            error="internal_error",
            code="INTERNAL_SERVER_ERROR",
            message=f"Error processing request: {str(e)}"
        )
        logger.save_response(500, error_response)
        logger.save()
        raise AppException(
            error_type="internal_error",
            code="INTERNAL_SERVER_ERROR",
            status_code=500,
            message=str(e)
        )

