#!/bin/bash
set -e

echo "🚀 Deploying Data Persistence Feature"
echo "=================================="

# Variables
PROJECT_ID="feisty-catcher-461000-g2"
VERSION="persistence-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="backups/$(date +%Y%m%d-%H%M%S)-pre-persistence"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Create backup
echo -e "${YELLOW}📦 Creating backup...${NC}"
mkdir -p $BACKUP_DIR
cp main.py $BACKUP_DIR/
cp -r src/components $BACKUP_DIR/
cp -r src/pages $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"

# Step 2: Update main.py imports
echo -e "${YELLOW}🔧 Updating imports...${NC}"
sed -i.bak 's/from data_persistence.parquet_handlers import/from data_persistence.parquet_handlers_fixed import/g' main.py
echo -e "${GREEN}✓ Imports updated${NC}"

# Step 3: Ensure pyarrow in requirements
echo -e "${YELLOW}📦 Updating requirements...${NC}"
if ! grep -q "pyarrow" requirements.txt; then
    echo "pyarrow==13.0.0" >> requirements.txt
    echo -e "${GREEN}✓ Added pyarrow to requirements.txt${NC}"
else
    echo -e "${GREEN}✓ pyarrow already in requirements.txt${NC}"
fi

# Step 4: Build frontend
echo -e "${YELLOW}🔨 Building frontend...${NC}"
cd audience-manager
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend built successfully${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi
cd ..

# Step 5: Copy Tobermory Web
echo -e "${YELLOW}📁 Integrating Tobermory Web...${NC}"
if [ -d "tobermory-web/build" ]; then
    cp -r tobermory-web/build/* audience-manager/build/
    echo -e "${GREEN}✓ Tobermory Web integrated${NC}"
else
    echo -e "${YELLOW}⚠ Tobermory Web build not found, skipping${NC}"
fi

# Step 6: Copy persistence handlers
echo -e "${YELLOW}📂 Setting up persistence handlers...${NC}"
mkdir -p data_persistence
cp data_persistence/parquet_handlers_fixed.py data_persistence/
echo -e "${GREEN}✓ Persistence handlers copied${NC}"

# Step 7: Run quick test
echo -e "${YELLOW}🧪 Running quick test...${NC}"
python -c "
try:
    from data_persistence.parquet_handlers_fixed import AudienceHandler
    print('✓ Persistence handlers import successfully')
except Exception as e:
    print(f'✗ Import error: {e}')
    exit(1)
"

# Step 8: Show deployment preview
echo ""
echo -e "${YELLOW}📋 Deployment Preview:${NC}"
echo "  Project: $PROJECT_ID"
echo "  Version: $VERSION"
echo "  Features:"
echo "    - Save Audience button"
echo "    - Saved Audiences page"
echo "    - Archive functionality"
echo "    - Thread-safe Parquet storage"
echo ""

# Step 9: Confirm deployment
read -p "Deploy to test version? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 1
fi

# Step 10: Deploy to test
echo -e "${YELLOW}🚀 Deploying to test version...${NC}"
gcloud app deploy app_production.yaml \
  --version=$VERSION \
  --no-promote \
  --quiet \
  --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Test deployment complete!${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Test URLs:${NC}"
    echo "  Main app: https://$VERSION-dot-$PROJECT_ID.ue.r.appspot.com"
    echo "  Activation Manager: https://$VERSION-dot-$PROJECT_ID.ue.r.appspot.com/activation-manager"
    echo ""
    echo -e "${YELLOW}📝 Test Checklist:${NC}"
    echo "  1. Login to the app"
    echo "  2. Create an audience through Natural Language"
    echo "  3. After segments appear, click 'Save Audience'"
    echo "  4. Navigate to /saved-audiences"
    echo "  5. Verify audience appears in list"
    echo "  6. Test archive functionality"
    echo ""
    echo -e "${YELLOW}🚀 To promote to production:${NC}"
    echo "  gcloud app services set-traffic default --splits=$VERSION=100 --project=$PROJECT_ID"
    echo ""
    echo -e "${YELLOW}↩️  To rollback if needed:${NC}"
    echo "  gcloud app services set-traffic default --splits=production=100 --project=$PROJECT_ID"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    echo "Restoring backup..."
    cp $BACKUP_DIR/main.py .
    exit 1
fi