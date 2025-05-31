#!/bin/bash

# Deploy minimal version for testing
echo "🚀 Deploying Minimal Test Version..."
echo "================================================"

# Deploy to staging
STAGING_VERSION="stg-minimal-$(date +%Y%m%d-%H%M%S)"
echo "Deploying staging version: $STAGING_VERSION"

gcloud app deploy app_cost_optimized.yaml \
    --version="$STAGING_VERSION" \
    --no-promote \
    --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test URLs:"
echo "  Test endpoint: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/test-deployment"
echo "  Health check: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/health"
echo ""