#!/bin/bash

# Deploy with fixed app.yaml
echo "🚀 Deploying with Fixed app.yaml..."
echo "================================================"

# Deploy to staging
STAGING_VERSION="stg-fixed-$(date +%Y%m%d-%H%M%S)"
echo "Deploying staging version: $STAGING_VERSION"

gcloud app deploy app_cost_optimized.yaml \
    --version="$STAGING_VERSION" \
    --no-promote \
    --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test URLs:"
echo "  Startup test: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/startup-test"
echo "  Test endpoint: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/test-deployment"
echo "  Health check: https://${STAGING_VERSION}-dot-feisty-catcher-461000-g2.appspot.com/api/health"
echo ""
echo "Check logs:"
echo "  gcloud app logs read --service=default --version=${STAGING_VERSION} --limit=50"