#!/bin/bash

# Vercel Deployment Script
set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Vercel Deployment Script ===${NC}"

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}Vercel CLI not found. Installing...${NC}"
    npm i -g vercel
fi

# GCP Backend URL
BACKEND_URL="https://audience-manager-api-593977832320.northamerica-northeast1.run.app"

# Create production env file
echo -e "${YELLOW}Creating production environment file...${NC}"
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
EOF

# Build the app
echo -e "${YELLOW}Building React app...${NC}"
npm run build

# Deploy to Vercel
echo -e "${YELLOW}Deploying to Vercel...${NC}"
echo -e "${BLUE}Note: You'll need to log in to Vercel if not already authenticated${NC}"

vercel --prod --yes

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Your app should be live at the URL provided by Vercel"
echo "2. Make sure GCP backend permissions are configured"
echo "3. Test the integration:"
echo "   - Check if the frontend loads"
echo "   - Try the Natural Language Audience Builder"
echo "   - Test API connectivity"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo "- If API calls fail, check GCP Cloud Run permissions"
echo "- Check browser console for CORS errors"
echo "- Verify environment variables in Vercel dashboard"