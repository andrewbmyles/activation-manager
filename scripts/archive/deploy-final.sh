#!/bin/bash

echo "🚀 Final Production Deployment"
echo "============================="

# Set project
gcloud config set project feisty-catcher-461000-g2

# Deploy to production
echo "📦 Deploying final production version..."
gcloud app deploy app_tobermory_final.yaml \
    --project=feisty-catcher-461000-g2 \
    --quiet \
    --version=production-final-$(date +%Y%m%d%H%M%S)

echo "✅ Deployment complete!"
echo ""
echo "🌐 Applications deployed:"
echo "   - Tobermory AI: https://tobermory.ai"
echo "   - Activation Manager: https://tobermory.ai/activation-manager"
echo "   - Password: demo2024"
echo ""
echo "📊 Features:"
echo "   - 40+ variables across 5 categories"
echo "   - Smart keyword search with relevance scoring"
echo "   - Natural language processing"
echo "   - Full platform integration"
echo "   - Clean, refactored codebase"