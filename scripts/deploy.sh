#!/bin/bash

# Define Project IDs
PROJECT_DEV="pipuli-dev"
PROJECT_PROD="pipuli-prod"
REGION="us-central1"

print_usage() {
  echo "Usage: ./scripts/deploy.sh [dev|prod|all]"
  exit 1
}

if [ "$1" == "" ]; then
  print_usage
fi

ENV=$1

if [ "$ENV" == "dev" ]; then
  PROJECT_ID=$PROJECT_DEV
  API_SERVICE="pipuli-api-dev"
  WEB_SERVICE="pipuli-web-dev"
elif [ "$ENV" == "prod" ]; then
  PROJECT_ID=$PROJECT_PROD
  API_SERVICE="pipuli-api-prod"
  WEB_SERVICE="pipuli-web-prod"
elif [ "$ENV" == "all" ]; then
  echo "🔥 Deploying to BOTH environments (Dev & Prod)..."
  ./scripts/deploy.sh dev
  ./scripts/deploy.sh prod
  exit 0
else
  print_usage
fi

echo "🚀 Starting Deployment to $ENV ($PROJECT_ID)..."

# Ensure Version Sync
echo "🔄 Syncing Versions..."
./scripts/set_version.sh

# Deploy API
echo "🐍 Deploying Backend (API)..."
gcloud run deploy $API_SERVICE \
  --source apps/api \
  --project $PROJECT_ID \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,SERVICE_NAME=$API_SERVICE,ENV=$ENV

# Get API URL
echo "🔍 Retrieving API URL..."
API_URL=$(gcloud run services describe $API_SERVICE --project $PROJECT_ID --region $REGION --format 'value(status.url)')
echo "✅ API URL found: $API_URL"

# Get API Key (Security Unification)
echo "🔑 Retrieving API Key from Secret Manager..."
API_KEY=$(gcloud secrets versions access latest --secret="api-key" --project "$PROJECT_ID")

# Deploy Web
# Deploy Web (Standard: Build Image -> Deploy Image)
# Using Artifact Registry (cloud-run-source-deploy repo) to match existing infra
# 2026-02-04: Added timestamp to tag to prevent "Zombie Revisions" (caching issues)
TIMESTAMP=$(date +%s)
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/$WEB_SERVICE:$TIMESTAMP"

echo "⚛️ Building Frontend Image (Web)..."

# Strategy Change: Generate .env.production locally and upload it
# This bypasses 'gcloud builds submit' limitations with --build-arg
echo "📝 Generating local .env.production..."
cat > apps/web/.env.production <<EOF
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_PROJECT_ID=$PROJECT_ID
NEXT_PUBLIC_API_KEY=$API_KEY
EOF

# Submit build (sources include the new .env.production)
gcloud builds submit apps/web \
  --tag $IMAGE_TAG \
  --project $PROJECT_ID

# Cleanup
rm apps/web/.env.production

echo "⚛️ Deploying Frontend Container..."
gcloud run deploy $WEB_SERVICE \
  --image $IMAGE_TAG \
  --project $PROJECT_ID \
  --region $REGION \
  --allow-unauthenticated

echo "✅ [$ENV] Deployment Complete! 🚀"
