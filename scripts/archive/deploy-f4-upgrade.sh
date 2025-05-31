#!/bin/bash

# Deploy with F4 instance for more memory
echo "🚀 Deploying with F4 Instance (1GB Memory)..."
echo "================================================"
echo "Previous: F2 (512MB) → New: F4 (1GB)"
echo ""

# Deploy to staging
STAGING_VERSION="stg-f4-$(date +%Y%m%d-%H%M%S)"
echo "Deploying staging version: $STAGING_VERSION"

gcloud app deploy app_cost_optimized.yaml \
    --version="$STAGING_VERSION" \
    --no-promote \
    --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test URLs:"
echo "  Health check: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/health"
echo "  Variable picker test: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/variable-picker/test"
echo "  Audiences: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/audiences?user_id=test"
echo ""
echo "Monitor startup:"
echo "  gcloud app logs tail --service=default --version=${STAGING_VERSION}"
echo ""
echo "Check for successful loader initialization:"
echo "  gcloud app logs read --service=default --version=${STAGING_VERSION} --limit=100 | grep -E '(Loaded.*variables|✅|❌)'"