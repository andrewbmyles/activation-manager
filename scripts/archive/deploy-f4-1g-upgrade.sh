#!/bin/bash

# Deploy with F4_1G instance for 2GB memory
echo "🚀 Deploying with F4_1G Instance (2GB Memory)..."
echo "================================================"
echo "Previous: F4 (1GB) → New: F4_1G (2GB)"
echo "Cost: $0.12/hour (vs $0.10/hour for F4)"
echo ""

# Deploy to staging
STAGING_VERSION="stg-f4-1g-$(date +%Y%m%d-%H%M%S)"
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
echo ""
echo "Monitor startup:"
echo "  gcloud app logs tail --service=default --version=${STAGING_VERSION}"