#!/bin/bash

# Demo Warmup Script
# Warms up the application before a demo to ensure fast first response

set -e

echo "🔥 WARMING UP APPLICATION FOR DEMO"
echo "==================================="
echo ""

# Application URL
APP_URL="https://feisty-catcher-461000-g2.nn.r.appspot.com"

echo "🌐 Testing application availability..."

# Health check
echo "📋 Checking health endpoint..."
curl -s "$APP_URL/health" > /dev/null && echo "✅ Health check passed" || echo "❌ Health check failed"

echo ""
echo "🔥 Warming up main application..."
curl -s "$APP_URL" > /dev/null && echo "✅ Main page warmed" || echo "❌ Main page failed"

echo ""
echo "🧠 Warming up API endpoints..."
curl -s -X POST "$APP_URL/api/nl/start_session" \
  -H "Content-Type: application/json" \
  -d '{}' > /dev/null && echo "✅ NL session endpoint warmed" || echo "⚠️  NL session endpoint may need attention"

echo ""
echo "🎯 Pre-loading embeddings (if enabled)..."
curl -s "$APP_URL/api/enhanced-variable-picker/search" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test warmup","top_k":5}' > /dev/null 2>&1 && echo "✅ Embeddings warmed" || echo "⚠️  Embeddings warming - may take a moment"

echo ""
echo "🎪 WARMUP COMPLETE!"
echo "==================="
echo ""
echo "✨ Your application is now warmed up and ready for demo"
echo "🚀 First demo request should be fast (< 2 seconds)"
echo "🎯 Demo URL: $APP_URL"
echo ""
echo "💡 Tip: Run this script 2-3 minutes before your demo starts"
echo "🎭 Break a leg with your demo!"