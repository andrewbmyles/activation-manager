#!/bin/bash

# Simplified Full GCP Deployment using Cloud Run source deploy
# This doesn't require Artifact Registry permissions

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

echo -e "${BLUE}=== Simplified Full Audience Manager Deployment ===${NC}"
echo -e "Using Cloud Run source deploy (no Docker/Artifact Registry required)"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo ""

# Deploy backend first
echo -e "${BLUE}Step 1: Deploying Backend API${NC}"
chmod +x ./deploy-backend-simple.sh
./deploy-backend-simple.sh

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend service to be ready...${NC}"
sleep 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe audience-manager-api \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}Error: Could not get backend URL${NC}"
    exit 1
fi

echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

# Update frontend environment with backend URL
echo -e "${YELLOW}Updating frontend environment...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_ENVIRONMENT=production
EOF

# Deploy frontend
echo -e "${BLUE}Step 2: Deploying Frontend${NC}"
chmod +x ./deploy-frontend-simple.sh
./deploy-frontend-simple.sh

# Wait for frontend to be ready
echo -e "${YELLOW}Waiting for frontend service to be ready...${NC}"
sleep 10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe audience-manager \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${RED}Error: Could not get frontend URL${NC}"
    exit 1
fi

# Test the deployment
echo -e "${YELLOW}Testing backend health endpoint...${NC}"
HEALTH_STATUS=$(curl -s ${BACKEND_URL}/health | grep -o '"status":"healthy"' || echo "failed")

if [[ "$HEALTH_STATUS" == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo -e "${BLUE}Your Applications:${NC}"
echo -e "Frontend: ${GREEN}${FRONTEND_URL}${NC}"
echo -e "Backend API: ${GREEN}${BACKEND_URL}${NC}"
echo ""
echo -e "${BLUE}Quick Test Commands:${NC}"
echo "# Test API health"
echo "curl ${BACKEND_URL}/health"
echo ""
echo "# Test frontend"
echo "curl -s ${FRONTEND_URL} | grep -o '<title>.*</title>'"
echo ""
echo -e "${BLUE}Cloud Console:${NC}"
echo "https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Visit ${FRONTEND_URL} to see your application"
echo "2. The Natural Language interface should be working"
echo "3. You can create audiences and export them"