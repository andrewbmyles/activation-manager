#!/bin/bash

# Deploy fix for variable picker routes
# This adds GET endpoints for better API compatibility

echo "🚀 Deploying Variable Picker Route Fixes..."
echo "================================================"

# Deploy to staging
STAGING_VERSION="stg-$(date +%Y%m%d-%H%M%S)"
echo "Deploying staging version: $STAGING_VERSION"

gcloud app deploy app_cost_optimized.yaml \
    --version="$STAGING_VERSION" \
    --no-promote \
    --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test URLs:"
echo "  Staging: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com"
echo ""
echo "Test the API:"
echo "  curl https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/health"
echo ""
echo "Run comprehensive tests:"
echo "  python test_staging_comprehensive.py"