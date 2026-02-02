# 🏗️ Infrastructure & Deployment Guide

This document details the complete setup for the Pipuli Monorepo infrastructure, covering Google Cloud Platform (GCP) resources, GitHub configuration, and deployment workflows for both Development and Production environments.

## 🌍 Environments

| Environment | Scope | GCP Project ID | Branch | Deployment URL | Config File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development** | Testing, Staging | `pipuli-dev` | `dev` | `https://pipuli-api-dev-[ID].run.app` | `apps/api/configs/dev.json` |
| **Production** | Live User Data | `pipuli-prod` | `main` | `https://pipuli-api-prod-[ID].run.app` | `apps/api/configs/prod.json` |

---

## ☁️ 1. Google Cloud Setup

### 1.1 Create Projects
Create two distinct projects in the [Google Cloud Console](https://console.cloud.google.com/):
- `pipuli-dev`
- `pipuli-prod`

Ensure **Billing** is enabled for both projects.

### 1.2 Enable APIs
Activate the following APIs for **BOTH** projects:
- **Cloud Run API**: Hosting the API container.
- **Cloud Firestore API**: NoSQL Database.
- **Secret Manager API**: Secure storage for keys.
- **Artifact Registry API**: Docker image storage.
- **Cloud Build API**: Building containers.

### 1.3 Configure Firestore
1. Go to **Firestore**.
2. Create Database in **Native Mode**.
3. Select Region: `us-central1` (or your preferred region).
4. Repeat for both envs.

### 1.4 Configure Secrets
Store sensitive keys in **Secret Manager**:

**In `pipuli-dev`:**
- `openai-api-key-dev`: Your OpenAI Test Key
- `sendgrid-api-key-dev`: SendGrid Test Key

**In `pipuli-prod`:**
- `openai-api-key-prod`: Your OpenAI Live Key
- `sendgrid-api-key-prod`: SendGrid Live Key

---

## 🛠️ 2. Database Initialization

We have a utility script to bootstrap the Firestore collections (`assets`, `movements`, etc.).

**Run locally:**
```bash
# Authenticate gcloud first
gcloud auth application-default login

# Setup DEV
ENV=dev python3 apps/api/utils/scripts/setup_firestore.py

# Setup PROD
ENV=prod python3 apps/api/utils/scripts/setup_firestore.py
```

---

## 📦 3. Manual Deployment

To manually deploy the API backend to Cloud Run:

### Development
```bash
gcloud run deploy pipuli-api-dev \
  --source apps/api \
  --project pipuli-dev \
  --region us-central1 \
  --set-env-vars ENV=dev \
  --allow-unauthenticated
```

### Production
```bash
gcloud run deploy pipuli-api-prod \
  --source apps/api \
  --project pipuli-prod \
  --region us-central1 \
  --set-env-vars ENV=prod \
  --allow-unauthenticated
```
*Note: `--allow-unauthenticated` makes the API public. Remove this flag if you want to restrict access to authenticated IAM users only.*

---

## 🐙 4. GitHub Workflow

### Branches
- **`dev`**: All development happens here. PRs merge into `dev`. Auto-deploys to `pipuli-dev` (future CI/CD).
- **`main`**: Production release. Merge `dev` -> `main` when stable. Auto-deploys to `pipuli-prod`.

### Repository Setup
1. Initialize repo: `git init`
2. Add remote: `git remote add origin https://github.com/pipulicom/pipuli-monorepo.git`
3. Push:
```bash
git branch -M main
git push -u origin main
git checkout -b dev
git push -u origin dev
git push -u origin dev
```

---

## 🔒 5. Security Hardening (Production)

For production environments, **DO NOT** use the generic "Editor" role for the Service Account. Instead, grant only the necessary granular permissions:

1.  **Cloud Run Admin** (`roles/run.admin`) - Manage services.
2.  **Service Account User** (`roles/iam.serviceAccountUser`) - Act as the service identity.
3.  **Artifact Registry Administrator** (`roles/artifactregistry.admin`) - Push Docker images.
4.  **Cloud Build Editor** (`roles/cloudbuild.builds.editor`) - Execute builds.
5.  **Storage Admin** (`roles/storage.admin`) - Manage build cache buckets.
6.  **Service Usage Consumer** (`roles/serviceusage.serviceUsageConsumer`) - Use project quota.
