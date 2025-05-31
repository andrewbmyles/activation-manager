#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🔧 Variable Picker Fix Deployment${NC}"
echo "================================"
echo "Fixing: Variable picker search in production"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="variable-picker-fix-${TIMESTAMP}"

echo -e "${YELLOW}📝 Changes being deployed:${NC}"
echo "  - Fixed parquet loader import"
echo "  - Updated .gcloudignore to include data files"
echo "  - Ensure CSV fallback works"
echo ""

# Check data files exist
echo -e "${BLUE}📦 Checking data files...${NC}"
if [ -f "data/Full_Variable_List_2022_CAN.csv" ]; then
    echo -e "${GREEN}✓ CSV file found${NC}"
else
    echo -e "${RED}✗ CSV file missing!${NC}"
    exit 1
fi

if [ -f "data/variables_2022_can.parquet" ]; then
    echo -e "${GREEN}✓ Parquet file found${NC}"
else
    echo -e "${YELLOW}⚠ Parquet file missing (will use CSV fallback)${NC}"
fi

echo -e "\n${YELLOW}🚀 Deploying to Google App Engine...${NC}"
gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Variable Picker fix deployed successfully!${NC}"
    echo -e "${GREEN}Version: $VERSION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📋 Fixed Issues:${NC}"
    echo "  ✓ Variable search now works with CSV data"
    echo "  ✓ Parquet fallback if available"
    echo "  ✓ Data files included in deployment"
    echo ""
    echo -e "${BLUE}🌐 Test the fix:${NC}"
    echo "  1. Go to https://tobermory.ai"
    echo "  2. Login and navigate to Natural Language Multi-Variate Audience Builder"
    echo "  3. Try searching for variables"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi