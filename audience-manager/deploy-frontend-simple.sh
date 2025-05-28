#!/bin/bash

# Simple Frontend Deployment using Cloud Run source deploy
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
SERVICE_NAME="audience-manager"

echo -e "${BLUE}=== Simple Frontend Deployment ===${NC}"
echo -e "Using Cloud Run source deploy (no Docker required)"
echo ""

# Build the React app first
echo -e "${YELLOW}Building React application...${NC}"
npm run build

# Create deployment directory
echo -e "${YELLOW}Creating frontend deployment directory...${NC}"
rm -rf frontend-deploy
mkdir -p frontend-deploy

# Copy build files
cp -r build/* frontend-deploy/

# Create a simple Express server to serve the React app
echo -e "${YELLOW}Creating server.js...${NC}"
cat > frontend-deploy/server.js << 'EOF'
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Serve static files
app.use(express.static(path.join(__dirname)));

// Handle React routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
EOF

# Create package.json for the server
echo -e "${YELLOW}Creating package.json...${NC}"
cat > frontend-deploy/package.json << 'EOF'
{
  "name": "audience-manager-frontend",
  "version": "1.0.0",
  "description": "Audience Manager Frontend",
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
EOF

# Deploy using source deploy
cd frontend-deploy
echo -e "${YELLOW}Deploying to Cloud Run (source deploy)...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

# Clean up
cd ..
rm -rf frontend-deploy

echo ""
echo -e "${GREEN}=== Frontend Deployment Complete ===${NC}"
echo -e "${GREEN}App URL: ${SERVICE_URL}${NC}"