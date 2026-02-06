"""
Main FastAPI application entry point.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gateway.router import router
from pathlib import Path

from configs.loader import load_config

# Load environment variables
load_dotenv()

# Read version
try:
    with open("VERSION", "r") as f:
        VERSION = f.read().strip()
except FileNotFoundError:
    VERSION = "0.0.0"

# Load Configuration
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pipuli-dev")
config = load_config(project_id)
cors_origins = config.get("security", {}).get("cors_origins", [])

app = FastAPI(
    title="Pipuli API",
    description="Generic backend for processing API calls from multiple frontend projects",
    version=VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include gateway router
app.include_router(router, prefix="/api", tags=["api"])


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from utils.exceptions import AppException
from response.formatter import error_response as format_error_response

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle application-specific logic errors.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            error=exc.error_type,
            code=exc.code,
            message=exc.message,
            params=exc.params,
            details=exc.details
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle automatic Pydantic validation errors.
    """
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            error="validation_error",
            code="VALIDATION_ERROR",
            message="Validation error",
            details={"errors": exc.errors()}  # Pydantic errors
        )
    )

    
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors.
    """
    # Log the error here if needed
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            error="internal_error",
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred."
        )
    )



@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "pipuli-api"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/version")
async def version():
    """Get application version."""
    return {
        "version": VERSION,
        "service": "pipuli-api"
    }

