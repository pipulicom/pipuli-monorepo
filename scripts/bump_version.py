#!/usr/bin/env python3
import sys

def bump_version(version_str):
    try:
        major, minor, patch = map(int, version_str.strip().split('.'))
        return f"{major}.{minor}.{patch + 1}"
    except ValueError:
        print(f"Error: Invalid version format '{version_str}'. expected X.Y.Z")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bump_version.py <version>")
        sys.exit(1)
    
    print(bump_version(sys.argv[1]))
