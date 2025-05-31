#!/bin/bash

# Deploy Ultra-Minimal Cost Configuration
# This script deploys the application with minimal resources for development/testing
# Uses the smallest possible instance class and disables embeddings

set -e

echo "🚀 Deploying Ultra-Minimal Cost Configuration..."
echo "📱 Frontend timeout: 60 seconds"
echo "💰 Instance class: F1 (smallest available)"
echo "📊 Max instances: 2"
echo "🔧 Embeddings: DISABLED (for maximum cost savings)"
echo ""

# Check if app_minimal_cost.yaml exists
if [ ! -f "app_minimal_cost.yaml" ]; then
    echo "❌ Error: app_minimal_cost.yaml not found!"
    exit 1
fi

# Deploy with minimal cost configuration
echo "🔄 Deploying to Google App Engine..."
gcloud app deploy app_minimal_cost.yaml --quiet

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: https://feisty-catcher-461000-g2.uw.r.appspot.com"
echo ""
echo "💡 Ultra-Minimal Configuration:"
echo "   • Instance class: F1 (smallest and cheapest)"
echo "   • Max instances: 2"
echo "   • Min instances: 0 (scales to zero when idle)"
echo "   • Embeddings: DISABLED"
echo "   • Very relaxed health checks"
echo ""
echo "⚠️  Note: This configuration disables embeddings for maximum cost savings."
echo "    Use this for testing or when embeddings are not needed."
echo "💰 Expected cost reduction: ~70-80% compared to original configuration"