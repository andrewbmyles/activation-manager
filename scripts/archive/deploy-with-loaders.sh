#!/bin/bash

# Deploy with variable loaders and error handling
echo "🚀 Deploying with Variable Loaders..."
echo "================================================"

# Deploy to staging
STAGING_VERSION="stg-loader-$(date +%Y%m%d-%H%M%S)"
echo "Deploying staging version: $STAGING_VERSION"

gcloud app deploy app_cost_optimized.yaml \
    --version="$STAGING_VERSION" \
    --no-promote \
    --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test URLs:"
echo "  Variable picker test: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/variable-picker/test"
echo "  Health check: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/health"
echo ""
echo "Check logs for loader status:"
echo "  gcloud app logs read --service=default --version=${STAGING_VERSION} --limit=50 | grep -E '(Pandas|Parquet|CSV|✅|❌)'"