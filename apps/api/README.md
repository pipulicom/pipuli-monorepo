# Pipuli API Service

This is the backend service for the **Pipuli Monorepo**, built with **FastAPI** and **Google Cloud Firestore**.

It serves as a centralized gateway for processing business workflows and managing data.

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

##  Version Management

The version is tracked in the `VERSION` file. Use the utility script to manage it:

```bash
# Show current version
python utils/version.py show

# Bump version
python utils/version.py patch  # 1.0.0 -> 1.0.1
python utils/version.py minor  # 1.0.0 -> 1.1.0
python utils/version.py major  # 1.0.0 -> 2.0.0
```

## 🚀 Deployment

The service is containerized using `Dockerfile` and deployed to **Google Cloud Run**.

```bash
gcloud run deploy stan-baas --source . --project stan-baas --region us-central1 --allow-unauthenticated
```
