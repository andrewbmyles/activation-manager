#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🔧 Backend HOTFIX Deployment${NC}"
echo "================================"
echo "Fixing: Enhanced variable picker API errors"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="backend-fix-${TIMESTAMP}"

echo -e "${YELLOW}🚀 Deploying backend fix...${NC}"
gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Backend fix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📋 Fixed Issues:${NC}"
    echo "  ✓ search_variables() now receives required query parameter"
    echo "  ✓ Proper fallback when enhanced picker not available"
    echo "  ✓ Correct response format for variable search"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi