"""
Main FastAPI application entry point.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gateway.router import router
from pathlib import Path

# Load environment variables
load_dotenv()

# Read version
try:
    with open("VERSION", "r") as f:
        VERSION = f.read().strip()
except FileNotFoundError:
    VERSION = "0.0.0"

app = FastAPI(
    title="Stan BaaS",
    description="Generic backend for processing API calls from multiple frontend projects",
    version=VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include gateway router
app.include_router(router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Pipuli Secure Deploy v1", "service": "stan-baas"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/version")
async def version():
    """Get application version."""
    return {
        "version": VERSION,
        "service": "stan-baas"
    }

