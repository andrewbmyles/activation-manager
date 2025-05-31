#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Activation Manager v1.4.0 Deployment${NC}"
echo "========================================"
echo -e "${GREEN}Natural Language Multi-Variate Audience Builder${NC}"
echo ""

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_NAME="v1-4-0-${TIMESTAMP}"
BACKUP_DIR="backups/${TIMESTAMP}-v1.4.0"

# Step 1: Pre-deployment checks
echo -e "\n${YELLOW}📋 Running pre-deployment checks...${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "audience-manager" ]; then
    echo -e "${RED}✗ Error: Not in the Activation Manager root directory${NC}"
    exit 1
fi

# Check for required files
echo "Checking required files..."
required_files=(
    "main.py"
    "requirements.txt"
    "app_production.yaml"
    "activation_manager/api/enhanced_variable_picker_api.py"
    "audience-manager/src/components/EnhancedNLAudienceBuilder.tsx"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All required files present${NC}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo "It's recommended to commit your changes before deploying."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Create comprehensive backup
echo -e "\n${YELLOW}📦 Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
cp main.py "$BACKUP_DIR/"
cp requirements.txt "$BACKUP_DIR/"
cp -r activation_manager "$BACKUP_DIR/"
cp -r audience-manager/src "$BACKUP_DIR/"
cp -r audience-manager/public "$BACKUP_DIR/"
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"

# Step 3: Verify v1.4.0 changes
echo -e "\n${YELLOW}🔍 Verifying v1.4.0 changes...${NC}"

# Check enhanced variable picker API
if grep -q "EnhancedVariablePickerAPI" main.py; then
    echo -e "${GREEN}✓ Enhanced Variable Picker API integrated${NC}"
else
    echo -e "${RED}✗ Enhanced Variable Picker API not found in main.py${NC}"
    exit 1
fi

# Check Natural Language Multi-Variate Audience Builder
if grep -q "Natural Language Multi-Variate Audience Builder" audience-manager/src/components/EnhancedNLAudienceBuilder.tsx; then
    echo -e "${GREEN}✓ Component renamed correctly${NC}"
else
    echo -e "${RED}✗ Component not renamed${NC}"
    exit 1
fi

# Check responsive UI classes
if grep -q "lg:w-80 xl:w-96" audience-manager/src/components/EnhancedNLAudienceBuilder.tsx; then
    echo -e "${GREEN}✓ Responsive UI scaling implemented${NC}"
else
    echo -e "${RED}✗ Responsive UI scaling not found${NC}"
    exit 1
fi

# Step 4: Clean build directories
echo -e "\n${YELLOW}🧹 Cleaning build directories...${NC}"
rm -rf audience-manager/build
rm -rf tobermory-web/build
rm -rf build
rm -rf __pycache__
find . -name "*.pyc" -delete
echo -e "${GREEN}✓ Build directories cleaned${NC}"

# Step 5: Build frontend
echo -e "\n${YELLOW}🔨 Building frontend...${NC}"
cd audience-manager

# Install dependencies if needed
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build with production environment
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend build successful${NC}"
    
    # Verify build integrity
    if [ -f "build/index.html" ] && [ -d "build/static" ]; then
        echo -e "${GREEN}✓ Build integrity verified${NC}"
    else
        echo -e "${RED}✗ Build integrity check failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Frontend build failed!${NC}"
    exit 1
fi
cd ..

# Step 6: Copy Tobermory Web build if available
echo -e "\n${YELLOW}📁 Checking for Tobermory Web integration...${NC}"
if [ -d "tobermory-web/build" ]; then
    # Don't overwrite index.html, just copy assets
    cp -r tobermory-web/build/static/* audience-manager/build/static/ 2>/dev/null || true
    echo -e "${GREEN}✓ Tobermory Web assets integrated${NC}"
else
    echo -e "${YELLOW}⚠ Tobermory Web build not found, skipping...${NC}"
fi

# Step 7: Test deployment
echo -e "\n${YELLOW}🧪 Deploying to test version...${NC}"
echo "Version: $VERSION_NAME"

# Create deployment record
DEPLOY_RECORD="deployments/${VERSION_NAME}.json"
mkdir -p deployments
cat > "$DEPLOY_RECORD" << EOF
{
  "version": "1.4.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "features": [
    "Natural Language Multi-Variate Audience Builder",
    "Responsive UI scaling",
    "Unified data sources",
    "Enhanced Variable Picker API integration"
  ]
}
EOF

# Deploy to test version
gcloud app deploy app_production.yaml \
  --version="$VERSION_NAME" \
  --no-promote \
  --quiet \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Test deployment successful!${NC}"
    echo ""
    echo -e "${BLUE}📍 Test URL:${NC}"
    echo "https://${VERSION_NAME}-dot-${PROJECT_ID}.ue.r.appspot.com"
    echo ""
    echo -e "${YELLOW}📋 Test Checklist for v1.4.0:${NC}"
    echo "  1. ✓ Login to the application"
    echo "  2. ✓ Navigate to 'Natural Language Multi-Variate Audience Builder'"
    echo "  3. ✓ Check UI scales properly on large screen (expand browser window)"
    echo "  4. ✓ Test variable search (e.g., 'young millennials who shop online')"
    echo "  5. ✓ Verify Enhanced Variable Picker API is being used (check network tab)"
    echo "  6. ✓ Test dynamic search refinement in step 4"
    echo "  7. ✓ Verify fallback works (disable backend temporarily)"
    echo "  8. ✓ Complete full workflow to distribution step"
    echo ""
    echo -e "${GREEN}🚀 To promote to production after testing:${NC}"
    echo "gcloud app versions migrate $VERSION_NAME --service=default --project=$PROJECT_ID"
    echo ""
    echo -e "${YELLOW}↩️  To rollback if needed:${NC}"
    echo "1. Restore from backup: cp -r $BACKUP_DIR/* ."
    echo "2. Rebuild and deploy previous version"
    echo ""
    echo -e "${BLUE}📊 To check deployment status:${NC}"
    echo "gcloud app versions list --project=$PROJECT_ID"
    
    # Save deployment info
    echo "$VERSION_NAME" > ".last_deployment"
    echo -e "\n${GREEN}📝 Deployment info saved to $DEPLOY_RECORD${NC}"
else
    echo -e "${RED}✗ Deployment failed! Check the error messages above.${NC}"
    echo -e "${YELLOW}Restoring from backup...${NC}"
    cp "$BACKUP_DIR/main.py" .
    exit 1
fi

echo -e "\n${GREEN}🎉 v1.4.0 deployment process complete!${NC}"