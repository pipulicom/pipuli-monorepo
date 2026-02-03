#!/bin/bash

# Wrapper for Git Commit & Push (Auto-Version bump)

if [ "$1" == "" ]; then
  echo "Usage: ./scripts/commit.sh \"your commit message\""
  exit 1
fi

MSG=$1

echo "📦 Staging all changes..."
git add .

echo "💾 Committing (Release Trigger)..."
# The pre-commit hook will handle version bumping if needed
git commit -m "$MSG"

# Check if commit succeeded (maybe nothing to commit)
if [ $? -eq 0 ]; then
  echo "🚀 Pushing to origin/dev..."
  git push origin dev
  echo "✅ Commit & Push Complete!"
else
  echo "⚠️ Commit failed (nothing to commit?)."
fi
