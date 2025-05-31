#!/bin/bash

# Final deployment solution - using zip file approach

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Final Deployment Solution${NC}"

PROJECT_ID="feisty-catcher-461000-g2"

# Step 1: Create a deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"

# Create temp directory
DEPLOY_DIR="gcp_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Copy essential files only
cp main.py $DEPLOY_DIR/
cp backend_gcp.py $DEPLOY_DIR/
cp -r audience-manager/build $DEPLOY_DIR/audience-manager/

# Create minimal requirements
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
Flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Copy variables JSON (not the large NPY files)
mkdir -p $DEPLOY_DIR/activation_manager/data/embeddings
cp activation_manager/data/embeddings/variables_full.json $DEPLOY_DIR/activation_manager/data/embeddings/ 2>/dev/null || echo "No variables file"
cp activation_manager/data/embeddings/variable_ids_full.json $DEPLOY_DIR/activation_manager/data/embeddings/ 2>/dev/null || echo "No IDs file"

# Create app.yaml in deploy directory
cat > $DEPLOY_DIR/app.yaml << 'EOF'
runtime: python311
instance_class: F1

automatic_scaling:
  min_instances: 0
  max_instances: 2

handlers:
- url: /static
  static_dir: audience-manager/build/static
  
- url: /
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html

- url: /api/.*
  script: auto

- url: /health
  script: auto

- url: /.*
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
EOF

# Step 2: Deploy from clean directory
cd $DEPLOY_DIR

echo -e "${YELLOW}Deploying from clean directory...${NC}"
echo -e "${BLUE}This avoids uploading unnecessary files${NC}"

# Try deployment with explicit project
gcloud app deploy app.yaml \
    --project=$PROJECT_ID \
    --quiet \
    --promote \
    --stop-previous-version

RESULT=$?
cd ..

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${BLUE}Your app is at: https://${PROJECT_ID}.appspot.com${NC}"
    echo -e "${YELLOW}Cleaning up...${NC}"
    rm -rf $DEPLOY_DIR
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Deploy directory preserved at: $DEPLOY_DIR${NC}"
    echo -e "${YELLOW}You can try manual deployment:${NC}"
    echo "cd $DEPLOY_DIR"
    echo "gcloud app deploy"
fi