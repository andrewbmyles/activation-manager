#!/bin/bash

# Activation Manager - GCP Deployment Script

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Activation Manager to Google Cloud Platform${NC}"

# Step 1: Authenticate if needed
echo -e "${YELLOW}Step 1: Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}Not authenticated. Please run: gcloud auth login${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated${NC}"

# Step 2: Set project
PROJECT_ID=$(gcloud config get-value project)
echo -e "${YELLOW}Step 2: Using project: $PROJECT_ID${NC}"

# Step 3: Enable required APIs
echo -e "${YELLOW}Step 3: Enabling required APIs...${NC}"
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}"

# Step 4: Check if App Engine is initialized
echo -e "${YELLOW}Step 4: Checking App Engine...${NC}"
if ! gcloud app describe >/dev/null 2>&1; then
    echo -e "${YELLOW}App Engine not initialized. Initializing in us-central...${NC}"
    gcloud app create --region=us-central
fi
echo -e "${GREEN}✓ App Engine ready${NC}"

# Step 5: Deploy application
echo -e "${YELLOW}Step 5: Deploying application...${NC}"
echo -e "${BLUE}This may take 5-10 minutes...${NC}"

gcloud app deploy app.yaml --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Get the app URL
    APP_URL="https://${PROJECT_ID}.appspot.com"
    echo -e "${BLUE}Your app is available at: ${APP_URL}${NC}"
    
    # Show logs command
    echo -e "${YELLOW}To view logs, run:${NC}"
    echo "gcloud app logs tail -s default"
    
    # Open in browser
    echo -e "${YELLOW}Opening in browser...${NC}"
    gcloud app browse
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Check the error messages above${NC}"
    exit 1
fi