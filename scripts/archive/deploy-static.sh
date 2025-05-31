#!/bin/bash

# Deploy static React app to Cloud Storage + CDN
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ID="feisty-catcher-461000-g2"
BUCKET_NAME="audience-manager-${PROJECT_ID}"
BACKEND_URL="https://audience-manager-api-593977832320.northamerica-northeast1.run.app"

echo -e "${BLUE}=== Static Site Deployment ===${NC}"

# Build the app
echo -e "${YELLOW}Building React app...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
GENERATE_SOURCEMAP=false
EOF

npm run build

# Create bucket if it doesn't exist
echo -e "${YELLOW}Creating storage bucket...${NC}"
gsutil mb -p ${PROJECT_ID} gs://${BUCKET_NAME} || true

# Enable public access
echo -e "${YELLOW}Configuring bucket...${NC}"
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}

# Upload files
echo -e "${YELLOW}Uploading files...${NC}"
gsutil -m rsync -r -d build/ gs://${BUCKET_NAME}/

# Set index and error pages
gsutil web set -m index.html -e index.html gs://${BUCKET_NAME}

# Get the URL
SITE_URL="https://storage.googleapis.com/${BUCKET_NAME}/index.html"

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Frontend URL: ${SITE_URL}${NC}"
echo -e "${GREEN}Backend URL: ${BACKEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Note: The backend may need IAM configuration for public access.${NC}"
echo "You can configure this in the Cloud Console."