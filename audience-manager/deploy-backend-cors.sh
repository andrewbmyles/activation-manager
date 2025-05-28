#!/bin/bash

# Deploy CORS-enabled backend to Cloud Run
set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
REGION="northamerica-northeast1"
SERVICE_NAME="audience-manager-api"

echo -e "${BLUE}=== Deploying CORS-Enabled Backend to Cloud Run ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo -e "Service: ${YELLOW}$SERVICE_NAME${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "gcp-backend" ]; then
    echo -e "${RED}Error: gcp-backend directory not found${NC}"
    exit 1
fi

# Deploy from source
echo -e "${YELLOW}Deploying backend with CORS support...${NC}"
cd gcp-backend

gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

cd ..

echo ""
echo -e "${GREEN}=== Backend Deployment Complete ===${NC}"
echo -e "${GREEN}API URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}Test Commands:${NC}"
echo "# Test health endpoint"
echo "curl ${SERVICE_URL}/health"
echo ""
echo "# Test API info"
echo "curl ${SERVICE_URL}/api"
echo ""
echo "# Test CORS preflight"
echo "curl -X OPTIONS ${SERVICE_URL}/api/nl/start_session \\"
echo "  -H 'Origin: https://audience-manager.vercel.app' \\"
echo "  -H 'Access-Control-Request-Method: POST' \\"
echo "  -H 'Access-Control-Request-Headers: Content-Type' -v"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update Vercel environment variable:"
echo "   REACT_APP_API_URL=${SERVICE_URL}"
echo "2. Redeploy on Vercel: vercel --prod --yes"