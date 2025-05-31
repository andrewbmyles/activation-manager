#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🔧 HOTFIX Deployment${NC}"
echo "========================"
echo "Fixing: Refine functionality and NL workflow text input"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="hotfix-${TIMESTAMP}"

# Quick checks
if [ ! -f "main.py" ] || [ ! -d "audience-manager" ]; then
    echo -e "${RED}✗ Error: Not in the Activation Manager root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Creating backup...${NC}"
mkdir -p "backups/hotfix-${TIMESTAMP}"
cp -r audience-manager/src/components/EnhancedNLAudienceBuilder.tsx "backups/hotfix-${TIMESTAMP}/"

echo -e "${YELLOW}🔨 Building frontend...${NC}"
cd audience-manager

# Quick build
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
cd ..

echo -e "${YELLOW}🚀 Deploying hotfix...${NC}"
gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Hotfix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME (promoted to production)${NC}"
    echo ""
    echo -e "${BLUE}🔍 Production URL:${NC} https://tobermory.ai"
    echo ""
    echo -e "${YELLOW}📋 Fixed Issues:${NC}"
    echo "  ✓ Refine button now works properly in step 4"
    echo "  ✓ Text input no longer gets stuck/disabled"
    echo "  ✓ Loading states properly managed"
    echo ""
    echo -e "${YELLOW}To rollback if needed:${NC}"
    echo "gcloud app versions migrate v1-4-0-20250528-231927 --service=default --project=$PROJECT_ID"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi