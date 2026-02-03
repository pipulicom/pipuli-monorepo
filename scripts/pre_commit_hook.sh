#!/bin/bash

# Pre-commit hook to auto-bump version if not modified

VERSION_FILE="VERSION"

# Check if VERSION is staged
if git diff --cached --name-only | grep -q "^$VERSION_FILE$"; then
    echo "ℹ️ Version manually updated. Proceeding..."
    exit 0
fi

echo "🤖 Auto-bumping version..."

# Get current version
CURRENT_VERSION=$(cat $VERSION_FILE)
# Bump version using python script
NEW_VERSION=$(python3 scripts/bump_version.py "$CURRENT_VERSION")

if [ $? -ne 0 ]; then
    echo "❌ Failed to bump version."
    exit 1
fi

# Write new version
echo "$NEW_VERSION" > $VERSION_FILE

# Sync other files
./scripts/set_version.sh

# Stage the version files
git add $VERSION_FILE apps/api/VERSION apps/web/package.json

echo "✅ Auto-bumped to $NEW_VERSION and added to commit."
exit 0
