#!/bin/bash

# Deploy using a pre-built sample container as a temporary solution
# This will at least get something running on Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
REGION="us-central1"  # Using us-central1 which seems more stable

echo -e "${BLUE}=== Deploying Sample Container to Test Cloud Run ===${NC}"
echo -e "This will deploy a simple 'Hello World' container to verify Cloud Run is working"
echo ""

# Deploy a pre-built public container (Cloud Run Hello sample)
echo -e "${YELLOW}Deploying sample container...${NC}"
gcloud run deploy audience-manager-test \
    --image gcr.io/cloudrun/hello \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe audience-manager-test --platform managed --region ${REGION} --format 'value(status.url)')

echo ""
echo -e "${GREEN}=== Test Deployment Complete ===${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}This is just a test container. If this works, we know Cloud Run is functioning.${NC}"
echo -e "${YELLOW}Next step would be to build and deploy your actual application.${NC}"