#!/usr/bin/env python3
"""
Version management script for Stan BaaS.

Usage:
    python scripts/update_version.py patch   # 1.0.0 -> 1.0.1
    python scripts/update_version.py minor   # 1.0.0 -> 1.1.0
    python scripts/update_version.py major   # 1.0.0 -> 2.0.0
    python scripts/update_version.py set 2.5.3  # Set specific version
"""
import sys
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "VERSION"


def read_version():
    """Read current version from VERSION file."""
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()


def write_version(version: str):
    """Write new version to VERSION file."""
    with open(VERSION_FILE, "w") as f:
        f.write(version + "\n")


def bump_version(bump_type: str):
    """
    Bump version based on type (major, minor, patch).
    
    Args:
        bump_type: One of 'major', 'minor', or 'patch'
    """
    current = read_version()
    major, minor, patch = map(int, current.split("."))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        print("   Use: major, minor, or patch")
        sys.exit(1)
    
    new_version = f"{major}.{minor}.{patch}"
    write_version(new_version)
    
    print(f"✅ Version updated: {current} → {new_version}")
    return new_version


def set_version(version: str):
    """
    Set specific version.
    
    Args:
        version: Version string (e.g., "1.2.3")
    """
    # Validate format
    parts = version.split(".")
    if len(parts) != 3:
        print(f"❌ Invalid version format: {version}")
        print("   Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)")
        sys.exit(1)
    
    try:
        major, minor, patch = map(int, parts)
    except ValueError:
        print(f"❌ Invalid version format: {version}")
        print("   All parts must be integers")
        sys.exit(1)
    
    current = read_version()
    write_version(version)
    
    print(f"✅ Version set: {current} → {version}")
    return version


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/update_version.py patch")
        print("  python scripts/update_version.py minor")
        print("  python scripts/update_version.py major")
        print("  python scripts/update_version.py set 2.5.3")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ["major", "minor", "patch"]:
        bump_version(command)
    elif command == "set":
        if len(sys.argv) < 3:
            print("❌ Missing version argument")
            print("   Usage: python scripts/update_version.py set 2.5.3")
            sys.exit(1)
        set_version(sys.argv[2])
    elif command == "show":
        current = read_version()
        print(f"Current version: {current}")
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: major, minor, patch, set, or show")
        sys.exit(1)


if __name__ == "__main__":
    main()
