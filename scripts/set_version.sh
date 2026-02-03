#!/bin/bash

# Reads version from root VERSION file
VERSION=$(cat VERSION)

echo "🔥 Synchronizing version to $VERSION..."

# 1. Update Backend (Ghost File - not allowed in git)
echo "$VERSION" > apps/api/VERSION
echo "✅ Backend updated (apps/api/VERSION - local only)"

# 2. Update Frontend (JSON)
# Using regex to replace version in package.json to avoid jq dependency requirement
sed -i '' "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" apps/web/package.json
echo "✅ Frontend updated (apps/web/package.json)"

echo "🚀 Version sync complete! Ready to commit."
