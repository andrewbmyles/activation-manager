#!/bin/bash

# Test unified search locally before deployment
# This allows testing the migration framework without deployment issues

echo "🧪 Testing Unified Search Locally"
echo "================================"

# Set environment variables for testing
export USE_UNIFIED_SEARCH=true
export UNIFIED_ROLLOUT_PERCENTAGE=50  # 50% for A/B testing

echo ""
echo "📋 Configuration:"
echo "  - USE_UNIFIED_SEARCH: $USE_UNIFIED_SEARCH"
echo "  - UNIFIED_ROLLOUT_PERCENTAGE: $UNIFIED_ROLLOUT_PERCENTAGE%"
echo ""

# Start the backend
echo "🚀 Starting backend with unified search enabled..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Run tests
echo ""
echo "🔍 Running tests..."
python test_unified_migration.py

# Check migration status
echo ""
echo "📊 Checking migration status..."
curl -s http://localhost:8080/api/search/migration/status | python3 -m json.tool

# Test routing for different users
echo ""
echo "🎯 Testing routing decisions..."
echo "User 1:"
curl -s -X POST http://localhost:8080/api/search/migration/test \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user001", "query": "test"}' | python3 -m json.tool

echo ""
echo "User 2:"
curl -s -X POST http://localhost:8080/api/search/migration/test \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user002", "query": "test"}' | python3 -m json.tool

# Test actual search
echo ""
echo "🔎 Testing actual search..."
curl -s -X POST http://localhost:8080/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -d '{"query": "contact with friends", "top_k": 10, "filter_similar": true}' | python3 -m json.tool | head -50

# Clean up
echo ""
echo "🧹 Cleaning up..."
kill $BACKEND_PID

echo ""
echo "✅ Local testing complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Review the test results above"
echo "  2. If tests pass, deploy with environment variables in app.yaml"
echo "  3. Monitor production metrics"