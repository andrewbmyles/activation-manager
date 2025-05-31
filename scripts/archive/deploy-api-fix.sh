#!/bin/bash
# Deploy API fix to staging

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-feisty-catcher-461000-g2}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="api-fix-${TIMESTAMP}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        API Fix Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo -e "${YELLOW}📝 Fixes being deployed:${NC}"
echo "  - Removed incorrect port 5000 reference"
echo "  - Ensuring API endpoints are accessible"
echo ""

# Build frontend with fix
echo -e "${YELLOW}Building frontend...${NC}"
cd audience-manager
npm run build
cd ..

echo -e "${GREEN}✓ Frontend built${NC}"

# Deploy to staging first
echo -e "${YELLOW}Deploying to staging for testing...${NC}"
STAGING_VERSION="stg-${VERSION_NAME}"

gcloud app deploy app_production.yaml \
  --version="${STAGING_VERSION}" \
  --no-promote \
  --quiet \
  --project="${PROJECT_ID}"

if [ $? -eq 0 ]; then
    STAGING_URL="https://${STAGING_VERSION}-dot-${PROJECT_ID}.appspot.com"
    
    echo -e "\n${GREEN}✅ API fix deployed to staging!${NC}"
    echo -e "Version: ${STAGING_VERSION}"
    echo -e "URL: ${BLUE}${STAGING_URL}${NC}"
    echo ""
    
    # Wait for deployment to be ready
    echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
    sleep 10
    
    # Run diagnostics
    echo -e "${YELLOW}Running API diagnostics...${NC}"
    ./debug-staging-api.sh "$STAGING_URL"
    
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test the Variable Picker at: ${STAGING_URL}"
    echo "2. If APIs work correctly, promote to production:"
    echo -e "   ${BLUE}./promote-to-prod.sh ${STAGING_VERSION}${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi