#!/bin/bash

# Prepare for Demo - Scale Up for Maximum Performance
# This script quickly scales up the application for demo presentations

set -e

echo "🎯 PREPARING FOR DEMO MODE"
echo "================================"
echo ""
echo "🚀 Upgrading to high-performance configuration..."
echo "💪 Instance class: F4_1G (maximum performance)"
echo "🔥 Min instances: 2 (always warm and ready)"
echo "⚡ Max instances: 5 (handles multiple demo users)"
echo "🎪 CPU threshold: 50% (aggressive scaling)"
echo "📦 Embeddings: Pre-loaded for instant responses"
echo ""

# Check if demo config exists
if [ ! -f "app_demo_ready.yaml" ]; then
    echo "❌ Error: app_demo_ready.yaml not found!"
    exit 1
fi

echo "⏳ Deploying demo configuration..."
gcloud app deploy app_demo_ready.yaml --quiet

echo ""
echo "🎉 DEMO MODE ACTIVATED!"
echo "================================"
echo ""
echo "✅ Your application is now optimized for demos"
echo "🌐 Demo URL: https://feisty-catcher-461000-g2.nn.r.appspot.com"
echo ""
echo "🎯 Demo Configuration Active:"
echo "   • F4_1G instances (high performance)"
echo "   • 2 instances always warm (instant response)"
echo "   • Aggressive scaling at 50% CPU"
echo "   • Pre-loaded embeddings (no cold start delays)"
echo "   • Optimized caching for fast UI loads"
echo ""
echo "⏱️  Expected Response Times:"
echo "   • First request: < 2 seconds"
echo "   • Subsequent requests: < 1 second"
echo "   • Variable search: < 5 seconds"
echo ""
echo "💰 Cost Impact: ~3x normal cost (only use during demos)"
echo ""
echo "🔄 To return to cost-optimized mode after demo:"
echo "   ./return-to-cost-optimized.sh"
echo ""
echo "🎪 READY FOR DEMO! Break a leg! 🎭"