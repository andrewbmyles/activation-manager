#!/bin/bash

# Return to Cost-Optimized Mode
# This script scales back down to cost-optimized configuration after demos

set -e

echo "💰 RETURNING TO COST-OPTIMIZED MODE"
echo "===================================="
echo ""
echo "📉 Scaling back to cost-optimized configuration..."
echo "💡 Instance class: F2 (cost-efficient)"
echo "🏠 Min instances: 0 (scales to zero when idle)"
echo "📊 Max instances: 3 (moderate scaling)"
echo "⚡ CPU threshold: 75% (efficient scaling)"
echo ""

# Check if cost-optimized config exists
if [ ! -f "app_cost_optimized.yaml" ]; then
    echo "❌ Error: app_cost_optimized.yaml not found!"
    exit 1
fi

echo "⏳ Deploying cost-optimized configuration..."
gcloud app deploy app_cost_optimized.yaml --quiet

echo ""
echo "✅ COST-OPTIMIZED MODE RESTORED!"
echo "===================================="
echo ""
echo "💰 Configuration Active:"
echo "   • F2 instances (cost-efficient)"
echo "   • Scales to 0 when idle (no idle costs)"
echo "   • 40-50% cost savings vs original config"
echo "   • 60-second frontend timeout buffer"
echo ""
echo "📊 Expected Performance:"
echo "   • Response times: < 60 seconds"
echo "   • Cost savings: ~$75-150/month vs demo mode"
echo "   • Automatic scaling based on demand"
echo ""
echo "🎯 Next Demo Preparation:"
echo "   ./prepare-for-demo.sh"
echo ""
echo "💡 Cost optimization active! 💰"