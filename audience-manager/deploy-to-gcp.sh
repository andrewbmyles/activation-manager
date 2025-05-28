#!/bin/bash

# GCP Cloud Run Deployment Script
# This script builds and deploys the Audience Manager to Google Cloud Run

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
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${SERVICE_NAME}"

echo -e "${BLUE}=== Audience Manager GCP Deployment ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo -e "Service: ${YELLOW}$SERVICE_NAME${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found. Please run this script from the audience-manager directory${NC}"
    exit 1
fi

# Build the React app
echo -e "${YELLOW}Building React application...${NC}"
npm run build

# Create a simple Dockerfile for Cloud Run
echo -e "${YELLOW}Creating Dockerfile...${NC}"
cat > Dockerfile.cloudrun << 'EOF'
# Multi-stage build for React app
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source files
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx configuration for Cloud Run
echo -e "${YELLOW}Creating nginx configuration...${NC}"
cat > nginx.conf << 'EOF'
server {
    listen 8080;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # Enable gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy (if backend is deployed)
    location /api {
        proxy_pass https://feisty-catcher-461000-g2.appspot.com;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Enable required APIs
echo -e "${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} -f Dockerfile.cloudrun .

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "NODE_ENV=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

# Clean up temporary files
rm -f Dockerfile.cloudrun nginx.conf

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Visit your app at: ${SERVICE_URL}"
echo "2. View logs: gcloud logs read --service=${SERVICE_NAME}"
echo "3. Monitor: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}To update environment variables:${NC}"
echo "gcloud run services update ${SERVICE_NAME} --update-env-vars KEY=VALUE --region ${REGION}"