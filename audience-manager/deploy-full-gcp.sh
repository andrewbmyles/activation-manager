#!/bin/bash

# Full GCP Deployment Script
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

# Deploy backend first
echo -e "${BLUE}Step 1: Deploying Backend API${NC}"
./deploy-backend-cloudrun.sh

# Get backend URL
BACKEND_URL=$(gcloud run services describe audience-manager-api --platform managed --region ${REGION} --format 'value(status.url)')

# Update frontend environment
echo -e "${YELLOW}Updating frontend environment...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_ENVIRONMENT=production
EOF

# Deploy frontend
echo -e "${BLUE}Step 2: Deploying Frontend${NC}"
./deploy-to-gcp.sh

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe audience-manager --platform managed --region ${REGION} --format 'value(status.url)')

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
echo "# View frontend logs"
echo "gcloud logs read --service=audience-manager --limit=50"
echo ""
echo "# View backend logs"
echo "gcloud logs read --service=audience-manager-api --limit=50"