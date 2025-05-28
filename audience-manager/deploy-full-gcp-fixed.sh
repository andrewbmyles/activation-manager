#!/bin/bash

# Fixed Full GCP Deployment Script
# Deploys both frontend and backend to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
REGION="northamerica-northeast1"

echo -e "${BLUE}=== Full Audience Manager GCP Deployment ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo ""

# First, ensure we're in the audience-manager directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: This script must be run from the audience-manager directory${NC}"
    exit 1
fi

# Enable required APIs first (with proper authentication check)
echo -e "${YELLOW}Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo -e "${RED}Error: Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

echo -e "${YELLOW}Setting project...${NC}"
gcloud config set project ${PROJECT_ID}

echo -e "${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project ${PROJECT_ID}

# Deploy backend first
echo -e "${BLUE}Step 1: Deploying Backend API${NC}"

# Check if deploy script exists and is executable
if [ ! -f "./deploy-backend-cloudrun.sh" ]; then
    echo -e "${RED}Error: deploy-backend-cloudrun.sh not found${NC}"
    exit 1
fi

chmod +x ./deploy-backend-cloudrun.sh
./deploy-backend-cloudrun.sh

# Wait a moment for the service to be fully deployed
echo -e "${YELLOW}Waiting for backend service to be ready...${NC}"
sleep 10

# Get backend URL with error handling
echo -e "${YELLOW}Getting backend URL...${NC}"
BACKEND_URL=$(gcloud run services describe audience-manager-api \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}Error: Could not get backend URL. Backend deployment may have failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

# Update frontend environment
echo -e "${YELLOW}Updating frontend environment...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_ENVIRONMENT=production
EOF

# Deploy frontend
echo -e "${BLUE}Step 2: Deploying Frontend${NC}"

# Check if deploy script exists and is executable
if [ ! -f "./deploy-to-gcp.sh" ]; then
    echo -e "${RED}Error: deploy-to-gcp.sh not found${NC}"
    exit 1
fi

chmod +x ./deploy-to-gcp.sh
./deploy-to-gcp.sh

# Wait a moment for the service to be fully deployed
echo -e "${YELLOW}Waiting for frontend service to be ready...${NC}"
sleep 10

# Get frontend URL with error handling
echo -e "${YELLOW}Getting frontend URL...${NC}"
FRONTEND_URL=$(gcloud run services describe audience-manager \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${RED}Error: Could not get frontend URL. Frontend deployment may have failed.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Full Deployment Complete ===${NC}"
echo -e "${GREEN}Frontend URL: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend URL: ${BACKEND_URL}${NC}"
echo ""
echo -e "${BLUE}Quick Links:${NC}"
echo "• App: ${FRONTEND_URL}"
echo "• API Health: ${BACKEND_URL}/health"
echo "• Cloud Console: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}Test Commands:${NC}"
echo "# Test API"
echo "curl ${BACKEND_URL}/health"
echo ""
echo "# Test frontend (should return HTML)"
echo "curl -s ${FRONTEND_URL} | head -n 10"
echo ""
echo "# View frontend logs"
echo "gcloud logs read --service=audience-manager --limit=50"
echo ""
echo "# View backend logs"
echo "gcloud logs read --service=audience-manager-api --limit=50"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo "• If services are not accessible, check IAM permissions"
echo "• Ensure billing is enabled for the project"
echo "• Check service logs for any errors"