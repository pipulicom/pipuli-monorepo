# Pipuli API Monorepo

Generic backend for processing API calls from multiple frontend projects.

## 📂 Structure

The codebase is organized for clarity and modularity:

- **`main.py`**: Application entry point.
- **`workflows/`**: Business logic. ONE file per workflow (e.g., `workflows/project_id/flow_name.py`).
- **`services/`**: Reusable infrastructure wrappers (Database, Auth, etc.).
- **`gateway/`**: Router and request handling logic.
- **`utils/`**: Shared utilities (Logger, Constants, Messages, Decorators).
- **`configs/`**: Project-specific configurations.

## 🛠️ Development

### Prerequisites
- Python 3.12+
- Google Cloud SDK (for Firestore/Secret Manager)

### Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Check Health**:
   - URL: `http://localhost:8000/health`

##  Version Management & Deployment

Please refer to the root `docs/infrastructure.md` or use the root scripts:

```bash
# Update version and sync
./scripts/set_version.sh

# Deploy
./scripts/deploy.sh [dev|prod|all]
```

