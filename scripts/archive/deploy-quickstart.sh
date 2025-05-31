#!/bin/bash

# Quick GCP Deployment using pre-built images
set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
PROJECT_ID="feisty-catcher-461000-g2"
REGION="northamerica-northeast1"

echo -e "${BLUE}=== Quick GCP Deployment ===${NC}"

# Deploy a simple backend using the sample hello service
echo -e "${YELLOW}Deploying backend API...${NC}"
gcloud run deploy audience-manager-api \
    --image gcr.io/cloudrun/hello \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "TARGET=Audience Manager API"

BACKEND_URL=$(gcloud run services describe audience-manager-api --platform managed --region ${REGION} --format 'value(status.url)')

# Deploy frontend using nginx
echo -e "${YELLOW}Building React app...${NC}"
npm run build

# Create deployment directory
mkdir -p deploy-temp
cd deploy-temp

# Copy build files
cp -r ../build/* .

# Create a simple nginx config
cat > default.conf << 'EOF'
server {
    listen       8080;
    server_name  localhost;
    
    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri /index.html;
    }
    
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
EOF

# Deploy using Cloud Build
echo -e "${YELLOW}Deploying frontend...${NC}"
gcloud run deploy audience-manager \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated

FRONTEND_URL=$(gcloud run services describe audience-manager --platform managed --region ${REGION} --format 'value(status.url)')

# Cleanup
cd ..
rm -rf deploy-temp

echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "Frontend: ${FRONTEND_URL}"
echo -e "Backend: ${BACKEND_URL}"