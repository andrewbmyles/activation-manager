#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 Deployment Health Check"
echo "========================="

# Check site accessibility
echo -n "Checking site availability... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://tobermory.ai/)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Site is up (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Site is down (HTTP $HTTP_CODE)${NC}"
fi

# Check static assets
echo -n "Checking static assets... "
MAIN_JS=$(curl -s https://tobermory.ai/ | grep -o 'main\.[a-z0-9]*\.js' | head -1)
if [ -n "$MAIN_JS" ]; then
    JS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://tobermory.ai/static/js/$MAIN_JS)
    if [ "$JS_CODE" = "200" ]; then
        echo -e "${GREEN}✓ JavaScript loading correctly${NC}"
    else
        echo -e "${RED}✗ JavaScript not loading (HTTP $JS_CODE)${NC}"
    fi
else
    echo -e "${RED}✗ Could not find JavaScript reference${NC}"
fi

# Check API health
echo -n "Checking API health... "
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://tobermory.ai/api/health)
if [ "$API_CODE" = "200" ]; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ API health check returned $API_CODE${NC}"
fi

# Check current version
echo -e "\n${YELLOW}Current deployment info:${NC}"
gcloud app versions list --service=default --project=feisty-catcher-461000-g2 --filter="TRAFFIC_SPLIT>0" --format="table(id,traffic_split,last_deployed)"

# Recent errors
echo -e "\n${YELLOW}Recent errors (if any):${NC}"
gcloud app logs read --service=default --limit=20 --project=feisty-catcher-461000-g2 | grep -i error | tail -5 || echo "No recent errors found"

echo -e "\n✅ Health check complete"