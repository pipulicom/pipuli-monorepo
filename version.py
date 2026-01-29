"""
Application version management.

This module reads the version from the VERSION file and provides
it as a constant that can be imported throughout the application.
"""
import os
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent

# Read version from VERSION file
VERSION_FILE = BASE_DIR / "VERSION"

def get_version() -> str:
    """
    Read and return the application version from VERSION file.
    
    Returns:
        Version string (e.g., "1.0.0")
    """
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"  # Fallback version

# Application version constant
__version__ = get_version()
VERSION = __version__

# Version components for programmatic access
VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = VERSION.split(".")
