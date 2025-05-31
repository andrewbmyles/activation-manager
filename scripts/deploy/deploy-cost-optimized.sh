#!/bin/bash

# Deploy Cost-Optimized Configuration
# This script deploys the application with reduced resource allocation
# taking advantage of the increased frontend timeout (60s)

set -e

echo "🚀 Deploying Cost-Optimized Configuration..."
echo "📱 Frontend timeout: 60 seconds"
echo "💰 Instance class: F2 (reduced from F4)"
echo "📊 Max instances: 3 (reduced from 10)"
echo "⚡ CPU threshold: 75% (increased from 65%)"
echo ""

# Check if app_cost_optimized.yaml exists
if [ ! -f "app_cost_optimized.yaml" ]; then
    echo "❌ Error: app_cost_optimized.yaml not found!"
    exit 1
fi

# Deploy with cost-optimized configuration
echo "🔄 Deploying to Google App Engine..."
gcloud app deploy app_cost_optimized.yaml --quiet

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: https://feisty-catcher-461000-g2.uw.r.appspot.com"
echo ""
echo "💡 Cost Optimizations Applied:"
echo "   • Reduced instance class: F4 → F2"
echo "   • Reduced max instances: 10 → 3"
echo "   • Min instances: 0 (scales to zero when idle)"
echo "   • Higher CPU threshold: 75% (less aggressive scaling)"
echo "   • Relaxed health checks (less frequent monitoring)"
echo ""
echo "⏱️  Frontend timeout: 60 seconds (allows for slower backend responses)"
echo "💰 Expected cost reduction: ~40-50% compared to previous configuration"