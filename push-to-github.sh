#!/bin/bash

# Script to push to GitHub while excluding Style folder

echo "🚀 Preparing to push to GitHub..."

# Make sure we're in the right directory
cd "/Users/myles/Documents/Activation Manager/audience-manager"

# Check if Style folder will be ignored
echo "✅ Checking .gitignore..."
if grep -q "/Style/" .gitignore; then
    echo "✅ Style folder is properly ignored"
else
    echo "❌ Style folder not in .gitignore!"
    exit 1
fi

# Add all files (respecting .gitignore)
echo "📦 Adding files..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status --short

# Confirm before commit
echo ""
read -p "Do you want to commit these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Commit
    echo "💾 Committing changes..."
    git commit -m "Update audience manager with enhanced features and deployment configs"
    
    # Push to GitHub
    echo "⬆️ Pushing to GitHub..."
    git push origin main
    
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 View your repo at: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')"
else
    echo "❌ Cancelled"
fi