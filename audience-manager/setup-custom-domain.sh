#!/bin/bash

# Custom Domain Setup Script for Audience Manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Custom Domain Setup for Audience Manager ===${NC}"
echo ""

# Get domain from user
read -p "Enter your domain (e.g., audiencemanager.com): " DOMAIN
read -p "Do you want to use api.$DOMAIN for the backend? (y/n): " USE_SUBDOMAIN

if [[ $USE_SUBDOMAIN == "y" ]]; then
    API_DOMAIN="api.$DOMAIN"
else
    read -p "Enter custom API domain: " API_DOMAIN
fi

REGION="northamerica-northeast1"

echo ""
echo -e "${YELLOW}Setting up domains:${NC}"
echo "Frontend: https://$DOMAIN"
echo "API: https://$API_DOMAIN"
echo ""

# Check if domain needs to be verified
echo -e "${YELLOW}Checking domain verification...${NC}"
VERIFIED=$(gcloud domains list-user-verified --format="value(id)" | grep "$DOMAIN" || echo "")

if [ -z "$VERIFIED" ]; then
    echo -e "${RED}Domain not verified!${NC}"
    echo "Please verify your domain first:"
    echo "1. Visit: https://console.cloud.google.com/apis/credentials/domainverification"
    echo "2. Add your domain and follow the verification steps"
    echo "3. Run this script again once verified"
    exit 1
fi

echo -e "${GREEN}Domain verified!${NC}"

# Map frontend domain
echo -e "${YELLOW}Mapping frontend to $DOMAIN...${NC}"
gcloud run domain-mappings create \
    --service=audience-manager \
    --domain=$DOMAIN \
    --region=$REGION || echo "Frontend mapping may already exist"

# Map API domain
echo -e "${YELLOW}Mapping API to $API_DOMAIN...${NC}"
gcloud run domain-mappings create \
    --service=audience-manager-api \
    --domain=$API_DOMAIN \
    --region=$REGION || echo "API mapping may already exist"

# Get DNS records
echo ""
echo -e "${BLUE}=== DNS Configuration Required ===${NC}"
echo -e "${YELLOW}Add these DNS records to your domain provider:${NC}"
echo ""

# Get frontend DNS records
echo -e "${GREEN}For $DOMAIN:${NC}"
gcloud run domain-mappings describe \
    --domain=$DOMAIN \
    --region=$REGION \
    --format="get(status.resourceRecords[])" 2>/dev/null | while IFS= read -r line; do
    TYPE=$(echo $line | grep -o 'type:[^ ]*' | cut -d: -f2)
    VALUE=$(echo $line | grep -o 'rrdata:[^ ]*' | cut -d: -f2)
    if [ ! -z "$TYPE" ] && [ ! -z "$VALUE" ]; then
        echo "Type: $TYPE"
        echo "Name: @ (or leave blank)"
        echo "Value: $VALUE"
        echo "---"
    fi
done

echo ""
echo -e "${GREEN}For $API_DOMAIN:${NC}"
echo "Type: CNAME"
echo "Name: api (or the subdomain part)"
echo "Value: ghs.googlehosted.com"
echo ""

# Ask about public access
echo -e "${YELLOW}Do you want to enable public access (no authentication required)? (y/n):${NC}"
read -p "" ENABLE_PUBLIC

if [[ $ENABLE_PUBLIC == "y" ]]; then
    echo -e "${YELLOW}Enabling public access...${NC}"
    
    # Enable public access for frontend
    gcloud run services add-iam-policy-binding audience-manager \
        --region=$REGION \
        --member="allUsers" \
        --role="roles/run.invoker" 2>/dev/null || \
        echo "Note: Public access may be restricted by organization policy"
    
    # Enable public access for API
    gcloud run services add-iam-policy-binding audience-manager-api \
        --region=$REGION \
        --member="allUsers" \
        --role="roles/run.invoker" 2>/dev/null || \
        echo "Note: Public access may be restricted by organization policy"
fi

# Update frontend with new API URL
echo -e "${YELLOW}Updating frontend configuration...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=https://$API_DOMAIN
REACT_APP_ENVIRONMENT=production
EOF

echo -e "${YELLOW}Do you want to rebuild and redeploy the frontend with the new API URL? (y/n):${NC}"
read -p "" REDEPLOY

if [[ $REDEPLOY == "y" ]]; then
    echo -e "${YELLOW}Building frontend...${NC}"
    npm run build
    
    echo -e "${YELLOW}Redeploying frontend...${NC}"
    # Create temporary deploy directory
    rm -rf frontend-deploy
    mkdir -p frontend-deploy
    cp -r build/* frontend-deploy/
    
    # Copy server files
    cat > frontend-deploy/package.json << 'EOFPKG'
{
  "name": "audience-manager-frontend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOFPKG

    cat > frontend-deploy/server.js << 'EOFSERVER'
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 8080;
app.use(express.static(path.join(__dirname)));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
EOFSERVER

    cd frontend-deploy
    gcloud run deploy audience-manager \
        --source . \
        --platform managed \
        --region $REGION \
        --no-allow-unauthenticated
    cd ..
    rm -rf frontend-deploy
fi

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Add the DNS records shown above to your domain provider"
echo "2. Wait for DNS propagation (5 minutes to 48 hours)"
echo "3. SSL certificates will be auto-provisioned (can take up to 24 hours)"
echo ""
echo -e "${YELLOW}Monitor progress:${NC}"
echo "gcloud run domain-mappings describe --domain=$DOMAIN --region=$REGION"
echo ""
echo -e "${GREEN}Your custom domains will be:${NC}"
echo "• Frontend: https://$DOMAIN"
echo "• API: https://$API_DOMAIN"
echo ""
echo -e "${YELLOW}Tip:${NC} Use Cloudflare for faster DNS propagation and additional features!"