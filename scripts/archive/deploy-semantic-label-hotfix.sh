#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🔧 Semantic Label Hotfix Deployment${NC}"
echo "====================================="
echo "Fixing: Always show brain icon and semantic label"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="semantic-label-hotfix-${TIMESTAMP}"

echo -e "${YELLOW}📝 Changes being deployed:${NC}"
echo "  - Brain icon (🧠) and 'semantic' label always visible"
echo "  - Applied to both search results and confirmed variables"
echo ""

# Build frontend
echo -e "${BLUE}🔨 Building frontend...${NC}"
cd audience-manager
npm run build
cd ..

if [ ! -d "audience-manager/build" ]; then
    echo -e "${RED}✗ Frontend build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"

echo -e "\n${YELLOW}🚀 Deploying to Google App Engine...${NC}"
gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Semantic label hotfix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📋 Fixed:${NC}"
    echo "  ✓ Brain icon (🧠) and 'semantic' label now always visible"
    echo "  ✓ Shows on all variable results"
    echo "  ✓ Shows on confirmed variables"
    echo ""
    echo -e "${BLUE}🌐 Test at: https://tobermory.ai${NC}"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi