#!/bin/bash

# Alternative deployment approach for GCP backend
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ID="feisty-catcher-461000-g2"
REGION="northamerica-northeast1"

echo -e "${BLUE}=== Alternative Backend Deployment ===${NC}"
echo ""
echo -e "${YELLOW}Since Cloud Build is having issues, here are alternative approaches:${NC}"
echo ""

echo -e "${BLUE}Option 1: Deploy using Cloud Shell${NC}"
echo "1. Go to: https://console.cloud.google.com/cloudshell/editor?project=${PROJECT_ID}"
echo "2. Upload the gcp-backend folder"
echo "3. In Cloud Shell, run:"
echo "   cd gcp-backend"
echo "   gcloud run deploy audience-manager-api --source . --region ${REGION} --allow-unauthenticated"
echo ""

echo -e "${BLUE}Option 2: Use a pre-deployed test backend${NC}"
echo "For testing, you can use this mock API endpoint that has CORS enabled:"
echo "https://httpbin.org"
echo ""

echo -e "${BLUE}Option 3: Deploy locally with ngrok${NC}"
echo "1. Run the backend locally:"
echo "   cd gcp-backend-simple"
echo "   pip install -r requirements.txt"
echo "   python app.py"
echo "2. In another terminal:"
echo "   ngrok http 8080"
echo "3. Use the ngrok URL in your Vercel app"
echo ""

echo -e "${BLUE}Option 4: Use Vercel Functions${NC}"
echo "We can migrate the backend to Vercel Functions (serverless)"
echo "This would keep everything in one place"
echo ""

echo -e "${YELLOW}For now, let's create a mock API that runs on Vercel:${NC}"