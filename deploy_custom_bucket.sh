#!/bin/bash

# Deploy with custom bucket

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying with custom bucket${NC}"

PROJECT_ID="feisty-catcher-461000-g2"
CUSTOM_BUCKET="activation-manager-deploy-${PROJECT_ID}"

# Create custom bucket
echo -e "${YELLOW}Creating custom bucket: gs://${CUSTOM_BUCKET}${NC}"
gsutil mb -p ${PROJECT_ID} gs://${CUSTOM_BUCKET} 2>/dev/null || echo "Bucket may already exist"

# Grant permissions
echo -e "${YELLOW}Granting permissions...${NC}"
gsutil iam ch allUsers:objectViewer gs://${CUSTOM_BUCKET}
gsutil iam ch serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:admin gs://${CUSTOM_BUCKET}

# Set the staging bucket
gcloud config set app/cloud_build_staging_bucket gs://${CUSTOM_BUCKET}

# Deploy
echo -e "${YELLOW}Deploying...${NC}"
gcloud app deploy app_simple.yaml \
    --quiet \
    --bucket gs://${CUSTOM_BUCKET} \
    --stop-previous-version

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Checking bucket permissions...${NC}"
    gsutil iam get gs://${CUSTOM_BUCKET}
fi