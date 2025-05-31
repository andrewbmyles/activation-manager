#!/bin/bash

# Fix GCP Deployment Issues

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing GCP Deployment Issues${NC}"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}"

# Step 2: Create staging bucket if it doesn't exist
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"
echo -e "${YELLOW}Step 2: Checking staging bucket: $BUCKET_NAME${NC}"

if ! gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    echo -e "${YELLOW}Creating staging bucket...${NC}"
    gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME
else
    echo -e "${GREEN}✓ Staging bucket exists${NC}"
fi

# Step 3: Grant permissions to service accounts
echo -e "${YELLOW}Step 3: Granting permissions to service accounts...${NC}"

# App Engine service account
APP_ENGINE_SA="${PROJECT_ID}@appspot.gserviceaccount.com"
echo -e "${BLUE}Granting access to App Engine service account: $APP_ENGINE_SA${NC}"
gsutil iam ch serviceAccount:${APP_ENGINE_SA}:roles/storage.objectAdmin gs://$BUCKET_NAME

# Cloud Build service account
CLOUD_BUILD_SA="${PROJECT_ID}@cloudbuild.gserviceaccount.com"
echo -e "${BLUE}Granting access to Cloud Build service account: $CLOUD_BUILD_SA${NC}"
gsutil iam ch serviceAccount:${CLOUD_BUILD_SA}:roles/storage.objectAdmin gs://$BUCKET_NAME

# Also grant Cloud Build service account App Engine deployer role
echo -e "${BLUE}Granting App Engine roles to Cloud Build...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/appengine.appAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/cloudbuild.builds.builder"

# Default compute service account (sometimes needed)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo -e "${BLUE}Granting access to Compute Engine service account: $COMPUTE_SA${NC}"
gsutil iam ch serviceAccount:${COMPUTE_SA}:roles/storage.objectAdmin gs://$BUCKET_NAME

echo -e "${GREEN}✓ Permissions granted${NC}"

# Step 4: Initialize App Engine if needed
echo -e "${YELLOW}Step 4: Checking App Engine...${NC}"
if ! gcloud app describe >/dev/null 2>&1; then
    echo -e "${YELLOW}App Engine not initialized. Please run:${NC}"
    echo "gcloud app create --region=us-central"
    exit 1
fi
echo -e "${GREEN}✓ App Engine ready${NC}"

# Step 5: Create a minimal Cloud Build configuration
echo -e "${YELLOW}Step 5: Creating Cloud Build configuration...${NC}"
cat > cloudbuild.yaml << EOF
steps:
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: 'bash'
  args:
  - '-c'
  - |
    echo "Build started"
    ls -la

timeout: 1200s
EOF
echo -e "${GREEN}✓ Cloud Build configuration created${NC}"

echo -e "\n${GREEN}✅ Fixes applied!${NC}"
echo -e "${YELLOW}Now try deploying again with:${NC}"
echo "gcloud app deploy app.yaml --quiet --verbosity=debug"
echo -e "\n${YELLOW}Or use the simplified deployment:${NC}"
echo "./deploy_simple_gcp.sh"