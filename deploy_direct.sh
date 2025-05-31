#!/bin/bash
# Direct deployment without Cloud Build

echo "Deploying directly to App Engine..."
echo "This bypasses Cloud Build and uploads directly"

# Deploy with no-promote first to test
gcloud app deploy app_minimal.yaml \
    --quiet \
    --no-promote \
    --version=test-$(date +%Y%m%d-%H%M%S) \
    --no-cache

if [ $? -eq 0 ]; then
    echo "Test deployment successful!"
    echo "To make it live, promote the version in the Cloud Console"
else
    echo "Deployment failed. Try the manual steps below."
fi
