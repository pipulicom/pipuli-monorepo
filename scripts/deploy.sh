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

# Deploy Web
echo "⚛️ Deploying Frontend (Web)..."
gcloud run deploy $WEB_SERVICE \
  --source apps/web \
  --project $PROJECT_ID \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_PROJECT_ID=$PROJECT_ID,NEXT_PUBLIC_API_URL=$API_URL

echo "✅ [$ENV] Deployment Complete! 🚀"
