#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Safe Production Deployment Script${NC}"
echo "======================================"

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="prod-${TIMESTAMP}"

# Step 1: Pre-deployment checks
echo -e "\n${YELLOW}📋 Running pre-deployment checks...${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "audience-manager" ]; then
    echo -e "${RED}✗ Error: Not in the Activation Manager root directory${NC}"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Create backup
echo -e "\n${YELLOW}📦 Creating backup...${NC}"
BACKUP_DIR="backups/${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"
cp main.py "$BACKUP_DIR/"
cp -r audience-manager/src "$BACKUP_DIR/"
cp -r audience-manager/public "$BACKUP_DIR/"
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"

# Step 3: Clean build directories to prevent conflicts
echo -e "\n${YELLOW}🧹 Cleaning build directories...${NC}"
rm -rf audience-manager/build
rm -rf tobermory-web/build
rm -rf audience-manager/node_modules/.cache
echo -e "${GREEN}✓ Build directories cleaned${NC}"

# Step 4: Install dependencies
echo -e "\n${YELLOW}📦 Checking dependencies...${NC}"
cd audience-manager
npm install --silent
cd ..
echo -e "${GREEN}✓ Dependencies up to date${NC}"

# Step 5: Build Activation Manager
echo -e "\n${YELLOW}🔨 Building Activation Manager...${NC}"
cd audience-manager
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✓ Build successful${NC}"

# Step 6: Verify build integrity
echo -e "\n${YELLOW}🔍 Verifying build integrity...${NC}"

# Check if index.html exists
if [ ! -f "audience-manager/build/index.html" ]; then
    echo -e "${RED}✗ index.html not found!${NC}"
    exit 1
fi

# Extract referenced JS/CSS files from index.html
MAIN_JS=$(grep -o 'main\.[a-z0-9]*\.js' audience-manager/build/index.html | head -1)
MAIN_CSS=$(grep -o 'main\.[a-z0-9]*\.css' audience-manager/build/index.html | head -1)

# Verify files exist
if [ ! -f "audience-manager/build/static/js/$MAIN_JS" ]; then
    echo -e "${RED}✗ JavaScript file not found: $MAIN_JS${NC}"
    exit 1
fi

if [ ! -f "audience-manager/build/static/css/$MAIN_CSS" ]; then
    echo -e "${RED}✗ CSS file not found: $MAIN_CSS${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build integrity verified${NC}"
echo "  - JS: $MAIN_JS"
echo "  - CSS: $MAIN_CSS"

# Step 7: Check for file conflicts
echo -e "\n${YELLOW}🔍 Checking for file conflicts...${NC}"
JS_COUNT=$(ls audience-manager/build/static/js/main.*.js 2>/dev/null | wc -l)
if [ "$JS_COUNT" -gt 1 ]; then
    echo -e "${RED}✗ Multiple main.js files detected! This will cause conflicts.${NC}"
    echo "Files found:"
    ls -la audience-manager/build/static/js/main.*.js
    exit 1
fi
echo -e "${GREEN}✓ No file conflicts detected${NC}"

# Step 8: Test server locally (optional)
echo -e "\n${YELLOW}🧪 Would you like to test locally first?${NC}"
read -p "Test locally? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting local server on port 8080...${NC}"
    echo "Press Ctrl+C when done testing"
    python main.py
fi

# Step 9: Deploy to test version
echo -e "\n${YELLOW}🚀 Deploying to test version...${NC}"
echo "Version: $VERSION_NAME-test"

gcloud app deploy app_production.yaml \
  --version="${VERSION_NAME}-test" \
  --no-promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    TEST_URL="https://${VERSION_NAME}-test-dot-${PROJECT_ID}.ue.r.appspot.com"
    echo -e "${GREEN}✓ Test deployment successful!${NC}"
    echo -e "${BLUE}Test URL: $TEST_URL${NC}"
    echo
    echo -e "${YELLOW}Please test the following:${NC}"
    echo "  1. Login functionality"
    echo "  2. Dashboard loads correctly"
    echo "  3. All pages are accessible"
    echo "  4. Semantic search works"
    echo "  5. No console errors"
    echo
    read -p "Does everything work correctly? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled. Test version remains available for debugging.${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Test deployment failed!${NC}"
    exit 1
fi

# Step 10: Deploy to production
echo -e "\n${YELLOW}🚀 Deploying to production...${NC}"
echo "Version: $VERSION_NAME"

gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Production deployment successful!${NC}"
    echo -e "${BLUE}Live URL: https://tobermory.ai${NC}"
    echo
    echo -e "${YELLOW}📊 Post-deployment checklist:${NC}"
    echo "  ✓ Version: $VERSION_NAME is now live"
    echo "  ✓ Backup saved in: $BACKUP_DIR"
    echo "  ✓ Test version available at: $TEST_URL"
    echo
    echo -e "${YELLOW}🔄 To rollback if needed:${NC}"
    echo "  1. Quick rollback to previous version:"
    echo "     ${GREEN}gcloud app versions list --project=$PROJECT_ID${NC}"
    echo "     ${GREEN}gcloud app versions migrate [PREVIOUS_VERSION] --service=default --project=$PROJECT_ID${NC}"
    echo
    echo "  2. Full rollback from backup:"
    echo "     ${GREEN}cp $BACKUP_DIR/main.py .${NC}"
    echo "     ${GREEN}cp -r $BACKUP_DIR/src/* audience-manager/src/${NC}"
    echo "     ${GREEN}./deploy-production-safe.sh${NC}"
else
    echo -e "${RED}✗ Production deployment failed!${NC}"
    echo "Test version is still available at: $TEST_URL"
    exit 1
fi

# Step 11: Create deployment record
echo -e "\n${YELLOW}📝 Creating deployment record...${NC}"
cat > "deployments/${TIMESTAMP}-deployment.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "version": "${VERSION_NAME}",
  "test_version": "${VERSION_NAME}-test",
  "deployed_by": "$(whoami)",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "backup_location": "${BACKUP_DIR}",
  "status": "success"
}
EOF
echo -e "${GREEN}✓ Deployment record created${NC}"

echo -e "\n${GREEN}🎉 Deployment complete!${NC}"