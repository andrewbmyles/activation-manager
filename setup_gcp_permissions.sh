#!/bin/bash

# Setup all GCP permissions correctly

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Setting up GCP permissions${NC}"

# Get project details
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"
echo -e "${YELLOW}Project Number: $PROJECT_NUMBER${NC}"

# Define service accounts
APP_ENGINE_SA="${PROJECT_ID}@appspot.gserviceaccount.com"
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
DEFAULT_SA="${PROJECT_ID}@appspot.gserviceaccount.com"

echo -e "\n${YELLOW}Service Accounts:${NC}"
echo -e "App Engine: $APP_ENGINE_SA"
echo -e "Cloud Build: $CLOUD_BUILD_SA"

# Create App Engine app if not exists
echo -e "\n${YELLOW}Checking App Engine...${NC}"
if ! gcloud app describe >/dev/null 2>&1; then
    echo -e "${RED}App Engine not initialized!${NC}"
    echo -e "${YELLOW}Please run: gcloud app create --region=us-central${NC}"
    exit 1
fi

# Setup staging bucket
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"
echo -e "\n${YELLOW}Setting up staging bucket: $BUCKET_NAME${NC}"

# Create bucket
if ! gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    gsutil mb -p $PROJECT_ID -l us-central1 gs://$BUCKET_NAME
fi

# Grant permissions using IAM commands that should work
echo -e "\n${YELLOW}Granting IAM permissions...${NC}"

# Grant App Engine permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEFAULT_SA}" \
    --role="roles/storage.objectAdmin" \
    --quiet

# For Cloud Build, use the numeric service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/storage.objectAdmin" \
    --quiet 2>/dev/null || echo "Cloud Build storage role may need manual setup"

echo -e "\n${GREEN}✅ Permissions setup complete!${NC}"
echo -e "${YELLOW}Now try deploying with:${NC}"
echo "./deploy_no_cloudbuild.sh"