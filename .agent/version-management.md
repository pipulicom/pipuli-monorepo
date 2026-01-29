# Version Management Guide

## Overview

This project uses **Semantic Versioning (SemVer)** with a centralized version management system.

## Files

- **`VERSION`**: Single source of truth for the application version
- **`version.py`**: Python module that reads VERSION file and exposes it as a constant
- **`scripts/update_version.py`**: Helper script to update versions
- **`main.py`**: FastAPI app uses VERSION constant

## Version Format

```
MAJOR.MINOR.PATCH
  1  .  2  .  3
```

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## How to Update Version

### Using the Script (Recommended)

```bash
# Bump patch (1.0.0 -> 1.0.1) - for bug fixes
python3 scripts/update_version.py patch

# Bump minor (1.0.0 -> 1.1.0) - for new features
python3 scripts/update_version.py minor

# Bump major (1.0.0 -> 2.0.0) - for breaking changes
python3 scripts/update_version.py major

# Set specific version
python3 scripts/update_version.py set 2.5.3

# Show current version
python3 scripts/update_version.py show
```

### Manual Update

Simply edit the `VERSION` file:

```bash
echo "1.2.3" > VERSION
```

The change will be automatically picked up by the application.

## Using Version in Code

```python
from version import VERSION

print(f"Current version: {VERSION}")
```

## API Endpoints

- **`GET /version`**: Returns current application version
  ```json
  {
    "version": "1.0.0",
    "service": "stan-baas"
  }
  ```

- **FastAPI Docs**: Version appears automatically in Swagger UI (`/docs`)

## For AI Agents

When asked to update the version:

1. **Determine bump type**:
   - Bug fix → `patch`
   - New feature → `minor`
   - Breaking change → `major`

2. **Run the script**:
   ```bash
   python3 scripts/update_version.py [patch|minor|major]
   ```

3. **No need to edit multiple files** - the VERSION file is the single source of truth

## Best Practices

1. **Always update VERSION before deploying**
2. **Tag releases in Git** with the version number (e.g., `v1.0.0`)
3. **Document changes** in commit messages
4. **Never skip versions** - follow sequential numbering
5. **Start at 1.0.0** for first stable release (currently at 1.0.0)

## Examples

```bash
# Bug fix release
python3 scripts/update_version.py patch
# 1.0.0 -> 1.0.1

# New feature
python3 scripts/update_version.py minor
# 1.0.1 -> 1.1.0

# Breaking change
python3 scripts/update_version.py major
# 1.1.0 -> 2.0.0
```
