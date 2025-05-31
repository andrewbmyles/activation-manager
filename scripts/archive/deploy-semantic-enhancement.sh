#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying Semantic Variable Picker Enhancement${NC}"
echo "=================================================="

# Get timestamp for versioning
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="backups/${TIMESTAMP}-pre-enhancement"
TEST_VERSION="test-semantic-${TIMESTAMP}"

# Step 1: Create backup
echo -e "\n${YELLOW}📦 Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
cp main.py "$BACKUP_DIR/"
cp -r audience-manager/src/components "$BACKUP_DIR/"
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"

# Step 2: Verify changes are in place
echo -e "\n${YELLOW}🔍 Verifying code changes...${NC}"
if grep -q "search_variables(query, 50)" main.py; then
    echo -e "${GREEN}✓ Backend changes confirmed (50 results)${NC}"
else
    echo -e "${RED}✗ Backend changes not found! Aborting.${NC}"
    exit 1
fi

# Step 3: Build frontend
echo -e "\n${YELLOW}🔨 Building frontend...${NC}"
cd audience-manager
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend build successful${NC}"
else
    echo -e "${RED}✗ Frontend build failed! Aborting.${NC}"
    exit 1
fi
cd ..

# Step 4: Copy Tobermory Web files
echo -e "\n${YELLOW}📁 Integrating Tobermory Web...${NC}"
if [ -d "tobermory-web/build" ]; then
    cp -r tobermory-web/build/* audience-manager/build/
    echo -e "${GREEN}✓ Tobermory Web integrated${NC}"
else
    echo -e "${YELLOW}⚠ Tobermory Web build directory not found, skipping...${NC}"
fi

# Step 5: Deploy to test version
echo -e "\n${YELLOW}🧪 Deploying to test version...${NC}"
echo "Version: $TEST_VERSION"

gcloud app deploy app_production.yaml \
  --version="$TEST_VERSION" \
  --no-promote \
  --quiet \
  --project=feisty-catcher-461000-g2

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test deployment complete!${NC}"
    echo -e "${GREEN}🔍 Test URL:${NC} https://${TEST_VERSION}-dot-feisty-catcher-461000-g2.ue.r.appspot.com"
    echo ""
    echo -e "${YELLOW}📋 Please test the following:${NC}"
    echo "  1. Login to the application"
    echo "  2. Navigate to Audience Builder"
    echo "  3. Use semantic search (e.g., 'millennials interested in sustainability')"
    echo "  4. Verify you see pagination controls when >10 results"
    echo "  5. Test 'Show All Variables' toggle"
    echo "  6. Select a variable and confirm no page redirect"
    echo ""
    echo -e "${YELLOW}🚀 To promote to production after testing:${NC}"
    echo -e "${GREEN}gcloud app versions migrate $TEST_VERSION --service=default --project=feisty-catcher-461000-g2${NC}"
    echo ""
    echo -e "${YELLOW}🔄 To rollback if needed:${NC}"
    echo -e "${GREEN}cp $BACKUP_DIR/main.py . && cp -r $BACKUP_DIR/components/* audience-manager/src/components/${NC}"
else
    echo -e "${RED}✗ Deployment failed! Check the error messages above.${NC}"
    exit 1
fi