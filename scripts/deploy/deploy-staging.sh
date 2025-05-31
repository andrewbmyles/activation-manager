#!/bin/bash
# Deploy to staging environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-feisty-catcher-461000-g2}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STAGING_VERSION="stg-${TIMESTAMP}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}       Staging Environment Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Version: ${STAGING_VERSION}"
echo -e "Project: ${PROJECT_ID}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ Google Cloud SDK is not installed${NC}"
    exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}✗ Not authenticated with Google Cloud${NC}"
    echo "Run: gcloud auth login"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites satisfied${NC}"
echo ""

# Check data files
echo -e "${YELLOW}Checking data files...${NC}"
if [ -f "data/Full_Variable_List_2022_CAN.csv" ]; then
    echo -e "${GREEN}✓ CSV data file found${NC}"
else
    echo -e "${RED}✗ CSV data file missing!${NC}"
    exit 1
fi
echo ""

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
cd audience-manager

# Clean previous build
rm -rf build

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
fi

# Build
npm run build || {
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
}

# Verify build
if [ ! -d "build" ]; then
    echo -e "${RED}✗ Build directory not created${NC}"
    exit 1
fi

cd ..
echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Deploy to staging (never promote)
echo -e "${YELLOW}Deploying to staging...${NC}"
gcloud app deploy app_production.yaml \
  --version="${STAGING_VERSION}" \
  --no-promote \
  --quiet \
  --project="${PROJECT_ID}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Staging deployment complete!${NC}"
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}Staging Environment Ready${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo -e "${YELLOW}Staging URL:${NC}"
    echo -e "${BLUE}https://${STAGING_VERSION}-dot-${PROJECT_ID}.appspot.com${NC}"
    echo ""
    echo -e "${YELLOW}View logs:${NC}"
    echo "gcloud app logs tail --version=${STAGING_VERSION}"
    echo ""
    echo -e "${YELLOW}Test the deployment:${NC}"
    echo "1. Open the staging URL above"
    echo "2. Run through the staging test checklist"
    echo "3. Check logs for any errors"
    echo ""
    echo -e "${YELLOW}To promote to production:${NC}"
    echo -e "${BLUE}./promote-to-prod.sh ${STAGING_VERSION}${NC}"
    echo ""
    echo -e "${GREEN}Happy testing! 🚀${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi