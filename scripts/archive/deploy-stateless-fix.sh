#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🔧 Variable Picker Stateless Fix Deployment${NC}"
echo "============================================"
echo "Fixing: Session state issues in production"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="stateless-fix-${TIMESTAMP}"

echo -e "${YELLOW}📝 Changes being deployed:${NC}"
echo "  - Made refine endpoint stateless (sends original_query from client)"
echo "  - Made confirm endpoint stateless (sends all_variables from client)"
echo "  - Made export endpoint stateless (POST with confirmed_variables)"
echo "  - Fixed multi-instance session storage issues"
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
    echo -e "\n${GREEN}✅ Variable Picker stateless fix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📋 Fixed Issues:${NC}"
    echo "  ✓ Refine now works in multi-instance production environment"
    echo "  ✓ Confirm functionality works without session state"
    echo "  ✓ Export functionality works without session state"
    echo "  ✓ All endpoints are now stateless and scalable"
    echo ""
    echo -e "${BLUE}🌐 Test the fix:${NC}"
    echo "  1. Go to https://tobermory.ai"
    echo "  2. Navigate to Natural Language Multi-Variate Audience Builder"
    echo "  3. Search for variables"
    echo "  4. Refine search should now work properly"
    echo "  5. Confirm and Export should work without errors"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi