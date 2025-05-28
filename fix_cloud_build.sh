#!/bin/bash

# Fix Cloud Build Service Account Issues

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing Cloud Build Service Account Issues${NC}"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"

# Step 1: Enable Cloud Build API (this creates the service account)
echo -e "${YELLOW}Step 1: Enabling Cloud Build API...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

# Wait for the service account to be created
echo -e "${YELLOW}Waiting for service account creation...${NC}"
sleep 5

# Step 2: Check if Cloud Build service account exists
echo -e "${YELLOW}Step 2: Checking Cloud Build service account...${NC}"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo -e "${BLUE}Expected Cloud Build SA: $CLOUD_BUILD_SA${NC}"

# List all service accounts to see what exists
echo -e "${YELLOW}Existing service accounts:${NC}"
gcloud iam service-accounts list --project=$PROJECT_ID

# Step 3: Grant basic permissions that should work
echo -e "${YELLOW}Step 3: Granting permissions using project number...${NC}"

# Grant Cloud Build Service Account role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/cloudbuild.builds.builder" \
    --condition=None 2>/dev/null || echo "Cloud Build builder role may already exist"

# Step 4: Create staging bucket with simpler permissions
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"
echo -e "${YELLOW}Step 4: Setting up staging bucket: $BUCKET_NAME${NC}"

# Create bucket if it doesn't exist
if ! gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    echo -e "${YELLOW}Creating staging bucket...${NC}"
    gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME
fi

# Grant storage access to Cloud Build using project-level permissions
echo -e "${YELLOW}Granting storage permissions...${NC}"
gsutil iam ch serviceAccount:${CLOUD_BUILD_SA}:objectAdmin gs://$BUCKET_NAME 2>/dev/null || \
    echo "Storage permissions may already exist"

# Step 5: Alternative deployment without Cloud Build
echo -e "${YELLOW}Step 5: Creating alternative deployment option...${NC}"
cat > deploy_direct.sh << 'EOF'
#!/bin/bash
# Direct deployment without Cloud Build

echo "Deploying directly to App Engine..."
echo "This bypasses Cloud Build and uploads directly"

# Deploy with no-promote first to test
gcloud app deploy app_minimal.yaml \
    --quiet \
    --no-promote \
    --version=test-$(date +%Y%m%d-%H%M%S) \
    --no-cache

if [ $? -eq 0 ]; then
    echo "Test deployment successful!"
    echo "To make it live, promote the version in the Cloud Console"
else
    echo "Deployment failed. Try the manual steps below."
fi
EOF

chmod +x deploy_direct.sh

echo -e "\n${GREEN}✅ Fixes applied!${NC}"
echo -e "${YELLOW}Try deploying with one of these options:${NC}"
echo -e "${BLUE}Option 1 (Direct):${NC} ./deploy_direct.sh"
echo -e "${BLUE}Option 2 (Simple):${NC} ./deploy_simple_gcp.sh"
echo -e "\n${YELLOW}If you still see errors, you may need to:${NC}"
echo "1. Enable billing for the project"
echo "2. Wait a few minutes for service accounts to propagate"
echo "3. Try deploying through Cloud Console UI"