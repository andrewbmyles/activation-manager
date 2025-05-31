#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🔧 Variable Picker Complete Fix Deployment${NC}"
echo "========================================="
echo "Fixing: Missing endpoints and page title"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="complete-fix-${TIMESTAMP}"

echo -e "${YELLOW}📝 Changes being deployed:${NC}"
echo "  - Added /api/variable-picker/refine/<session_id> endpoint"
echo "  - Added /api/variable-picker/confirm/<session_id> endpoint"
echo "  - Added /api/variable-picker/export/<session_id> endpoint"
echo "  - Updated page title to 'Natural Language Multi-Variate Audience Builder'"
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
    echo -e "\n${GREEN}✅ Variable Picker complete fix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📋 Fixed Features:${NC}"
    echo "  ✓ Refine search now works properly"
    echo "  ✓ Confirm variables functionality added"
    echo "  ✓ Export to JSON/CSV functionality added"
    echo "  ✓ Page title shows 'Natural Language Multi-Variate Audience Builder'"
    echo ""
    echo -e "${BLUE}🌐 Test the fix:${NC}"
    echo "  1. Go to https://tobermory.ai"
    echo "  2. Navigate to Natural Language Multi-Variate Audience Builder"
    echo "  3. Search for variables"
    echo "  4. Try the 'Refine' feature"
    echo "  5. Select variables and 'Confirm'"
    echo "  6. Export results as JSON or CSV"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi