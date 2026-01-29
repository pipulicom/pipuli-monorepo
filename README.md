# Stan BaaS (Backend-as-a-Service)

A centralized, modular backend infrastructure designed to serve multiple frontend projects with a unified API gateway, structured logging, and isolated resources.

## 📚 Documentation

For AI agents and developers, see **[`.agent/`](.agent/)** directory for:
- Code patterns and standards
- Architecture decisions
- Example templates

## 🔢 Version Management

Current version: **1.0.0** (see [`VERSION`](VERSION) file)

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Update Version

```bash
# Bump patch version (1.0.0 -> 1.0.1)
python scripts/update_version.py patch

# Bump minor version (1.0.0 -> 1.1.0)
python scripts/update_version.py minor

# Bump major version (1.0.0 -> 2.0.0)
python scripts/update_version.py major

# Set specific version
python scripts/update_version.py set 2.5.3

# Show current version
python scripts/update_version.py show
```

### Check Version

```bash
# Via API
curl https://stan-baas-560010446261.us-central1.run.app/version

# Via file
cat VERSION
```

## 🚀 Active Projects

| Project ID | Database | Status |
|------------|----------|--------|
| `stan-baas-admin` | `stan-baas-admin-db` | ✅ Active |
| `pipuli-asset-mngmt` | `pipuli-asset-mngmt-db` | ✅ Active |

## 📡 Available Endpoints

### Pipuli Asset Management

**Assets:**
- `POST /api/pipuli-asset-mngmt/create_asset` - Create new asset
- `POST /api/pipuli-asset-mngmt/update_asset` - Update existing asset
- `POST /api/pipuli-asset-mngmt/delete_asset` - Soft-delete asset

**Movements:**
- `POST /api/pipuli-asset-mngmt/create_asset_movement` - Create movement
- `POST /api/pipuli-asset-mngmt/update_asset_movement` - Update movement
- `POST /api/pipuli-asset-mngmt/delete_asset_movement` - Soft-delete movement
- `POST /api/pipuli-asset-mngmt/get_asset_movements` - List movements

**Dashboard:**
- `POST /api/pipuli-asset-mngmt/get_user_dashboard` - Get dashboard data
- `POST /api/pipuli-asset-mngmt/consolidate_month` - Consolidate monthly data

**Auth:**
- `POST /api/pipuli-asset-mngmt/auth_login` - User authentication

## Quick Start

**Deploy:**
```bash
gcloud run deploy stan-baas --source . --project stan-baas --region us-central1 --allow-unauthenticated
```

**Health Check:**
```bash
curl https://stan-baas-560010446261.us-central1.run.app/health
```
