#!/bin/bash

# Quick Deploy Script for Audience Manager
# This script will guide you through the deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   Audience Manager - Quick Deploy Assistant    ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js installed${NC} ($(node --version))"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

# Check if gcloud is installed
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✓ Google Cloud SDK installed${NC}"
else
    echo -e "${RED}✗ Google Cloud SDK not found${NC}"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if vercel is installed
if command -v vercel &> /dev/null; then
    echo -e "${GREEN}✓ Vercel CLI installed${NC}"
else
    echo -e "${YELLOW}⚠ Vercel CLI not found. Installing...${NC}"
    npm i -g vercel
fi

echo ""
echo -e "${BLUE}Let's set up your deployment!${NC}"
echo ""

# Get GCP Project ID
echo -e "${YELLOW}Step 1: Google Cloud Project${NC}"
echo "Enter your GCP Project ID (or press Enter to create a new one):"
read -p "> " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    # Generate a unique project ID
    PROJECT_ID="audience-manager-$(date +%s)"
    echo -e "${YELLOW}Creating new project: $PROJECT_ID${NC}"
    echo ""
    echo "Run this command to create the project:"
    echo -e "${CYAN}gcloud projects create $PROJECT_ID --name=\"Audience Manager\"${NC}"
    echo ""
    echo "Press Enter after creating the project..."
    read
fi

# Set the project
echo ""
echo "Run this command to set your project:"
echo -e "${CYAN}gcloud config set project $PROJECT_ID${NC}"
echo ""
echo "Press Enter after running the command..."
read

# Enable APIs
echo ""
echo -e "${YELLOW}Step 2: Enable Required APIs${NC}"
echo "Run this command to enable the required APIs:"
echo -e "${CYAN}gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com redis.googleapis.com storage.googleapis.com${NC}"
echo ""
echo "Press Enter after running the command..."
read

# Create App Engine app
echo ""
echo -e "${YELLOW}Step 3: Create App Engine Application${NC}"
echo "Run this command to create an App Engine app:"
echo -e "${CYAN}gcloud app create --region=us-central1${NC}"
echo ""
echo "Press Enter after running the command (skip if already exists)..."
read

# Create sample data
echo ""
echo -e "${YELLOW}Step 4: Prepare Sample Data${NC}"
echo "Creating sample dataset..."
cd src/api
python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('.'))))
from enhanced_nl_audience_builder import DataRetriever
dr = DataRetriever('', '')
df = dr.fetch_data(['AGE_RANGE', 'INCOME_LEVEL', 'LOCATION_TYPE', 'PURCHASE_FREQUENCY', 'SUSTAINABILITY_SCORE'], 1000)
df.to_csv('../../gcp/sample_data.csv', index=False)
print('Sample data created successfully!')
" || echo -e "${YELLOW}Note: Sample data creation failed. You can upload your own data later.${NC}"
cd ../..

# Deploy backend
echo ""
echo -e "${YELLOW}Step 5: Deploy Backend to GCP${NC}"
echo "We'll now deploy the backend. Run these commands:"
echo ""
echo -e "${CYAN}cd gcp${NC}"
echo -e "${CYAN}gcloud app deploy app.yaml --quiet${NC}"
echo ""
echo "Press Enter after deployment completes..."
read

# Get backend URL
BACKEND_URL="https://$PROJECT_ID.appspot.com"
echo ""
echo -e "${GREEN}✓ Backend deployed at: $BACKEND_URL${NC}"

# Test backend
echo ""
echo "Let's test the backend. Run this command:"
echo -e "${CYAN}curl $BACKEND_URL/health${NC}"
echo ""
echo "Press Enter after testing..."
read

# Deploy frontend
echo ""
echo -e "${YELLOW}Step 6: Deploy Frontend to Vercel${NC}"
echo "We'll now deploy the frontend."
echo ""
echo "First, let's update the environment variable:"
echo -e "${CYAN}echo 'REACT_APP_API_URL=$BACKEND_URL' > .env.production.local${NC}"
echo ""

# Create env file
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production.local

echo "Now run this command to deploy to Vercel:"
echo -e "${CYAN}vercel --prod${NC}"
echo ""
echo "When prompted by Vercel:"
echo "1. Link to your Vercel account"
echo "2. Set up as a new project"
echo "3. Use the default settings"
echo "4. Add this environment variable when asked:"
echo "   ${YELLOW}REACT_APP_API_URL = $BACKEND_URL${NC}"
echo ""
echo "Press Enter after Vercel deployment completes..."
read

# Summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}        Deployment Complete! 🎉                 ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Your application is now live at:${NC}"
echo -e "Backend API: ${YELLOW}$BACKEND_URL${NC}"
echo -e "Frontend: ${YELLOW}[Check Vercel output above]${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "View backend logs: ${CYAN}gcloud app logs tail -s default${NC}"
echo -e "Redeploy backend: ${CYAN}cd gcp && gcloud app deploy${NC}"
echo -e "Redeploy frontend: ${CYAN}vercel --prod${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test your application"
echo "2. Upload your full dataset to GCS (optional)"
echo "3. Set up monitoring and alerts"
echo "4. Configure custom domain (optional)"
echo ""
echo -e "${GREEN}Congratulations on your deployment! 🚀${NC}"