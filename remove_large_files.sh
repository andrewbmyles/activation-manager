#!/bin/bash

echo "Removing large files from git history..."

# Remove large files from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch activation_manager/data/embeddings/variable_embeddings_full.npy activation_manager/data/embeddings/all_variable_embeddings.parquet data/embeddings/*.npy data/embeddings/*.parquet' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Large files removed from history."
echo "Now force push with: git push origin main --force"