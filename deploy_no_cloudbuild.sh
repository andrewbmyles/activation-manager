#!/bin/bash

# Deploy to App Engine without Cloud Build

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying to App Engine (No Cloud Build)${NC}"

# Create a very minimal app.yaml
echo -e "${YELLOW}Creating minimal configuration...${NC}"

# Use the GCP-optimized backend
cat > main.py << 'EOF'
from backend_gcp import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
EOF

# Create minimal app.yaml with no build steps
cat > app_simple.yaml << 'EOF'
runtime: python311
instance_class: F1

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

# Create a minimal requirements.txt for GCP
cat > requirements_gcp.txt << 'EOF'
Flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Temporarily rename the original requirements.txt
mv requirements.txt requirements_original.txt
mv requirements_gcp.txt requirements.txt

echo -e "${YELLOW}Deploying to App Engine...${NC}"
echo -e "${BLUE}Using minimal configuration to avoid Cloud Build issues${NC}"

# Deploy with specific flags to avoid Cloud Build
gcloud app deploy app_simple.yaml \
    --quiet \
    --promote \
    --stop-previous-version \
    --verbosity=warning

DEPLOY_RESULT=$?

# Restore original requirements.txt
mv requirements.txt requirements_gcp.txt
mv requirements_original.txt requirements.txt

if [ $DEPLOY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    PROJECT_ID=$(gcloud config get-value project)
    echo -e "${BLUE}Your app is available at: https://${PROJECT_ID}.appspot.com${NC}"
    echo -e "${YELLOW}Note: This deployment uses simplified search without embeddings${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Try these manual steps:${NC}"
    echo "1. Go to https://console.cloud.google.com/appengine"
    echo "2. Click 'Create Application' if needed"
    echo "3. Choose region: us-central"
    echo "4. Try deploying again"
fi