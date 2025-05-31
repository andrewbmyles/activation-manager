#!/bin/bash
# Debug API issues in staging

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide staging URL${NC}"
    echo "Usage: $0 https://stg-VERSION-dot-PROJECT.appspot.com"
    exit 1
fi

STAGING_URL="$1"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        Staging API Diagnostics${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Testing: ${STAGING_URL}"
echo ""

# Test 1: Basic connectivity
echo -e "${YELLOW}1. Testing basic connectivity...${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${STAGING_URL}" || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Site is reachable${NC}"
else
    echo -e "${RED}✗ Site returned HTTP $RESPONSE${NC}"
fi

# Test 2: Health endpoint
echo -e "\n${YELLOW}2. Testing health endpoint...${NC}"
HEALTH=$(curl -s "${STAGING_URL}/api/health" || echo "{}")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health endpoint working${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}✗ Health endpoint not responding${NC}"
    echo "Response: $HEALTH"
fi

# Test 3: Variable picker start endpoint
echo -e "\n${YELLOW}3. Testing variable picker API...${NC}"
PICKER_RESPONSE=$(curl -s -X POST "${STAGING_URL}/api/variable-picker/start" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}' || echo "{}")

if echo "$PICKER_RESPONSE" | grep -q "session_id"; then
    echo -e "${GREEN}✓ Variable picker API working${NC}"
    echo "$PICKER_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}✗ Variable picker API error${NC}"
    echo "Response: $PICKER_RESPONSE"
fi

# Test 4: Check embeddings status
echo -e "\n${YELLOW}4. Testing embeddings status...${NC}"
EMBEDDINGS=$(curl -s "${STAGING_URL}/api/embeddings-status" || echo "{}")
if echo "$EMBEDDINGS" | grep -q "status"; then
    echo -e "${GREEN}✓ Embeddings endpoint working${NC}"
    echo "$EMBEDDINGS" | python3 -m json.tool 2>/dev/null || echo "$EMBEDDINGS"
else
    echo -e "${RED}✗ Embeddings endpoint error${NC}"
fi

# Test 5: Check logs for errors
echo -e "\n${YELLOW}5. Recent error logs:${NC}"
echo "Run this command to see staging logs:"
echo -e "${BLUE}gcloud app logs read --service=default --version=${STAGING_URL##*/} --limit=20 | grep -i error${NC}"

echo -e "\n${BLUE}================================================${NC}"
echo -e "${YELLOW}Diagnostics complete!${NC}"
echo ""
echo "Common issues:"
echo "1. If all endpoints fail: Check if deployment completed"
echo "2. If health works but APIs fail: Check data files deployment"
echo "3. If 'session_id' missing: Check variable data loading"
echo ""
echo "View full logs with:"
VERSION=$(echo "$STAGING_URL" | sed 's/.*\/\///; s/-dot-.*//')
echo -e "${BLUE}gcloud app logs tail --version=$VERSION${NC}"