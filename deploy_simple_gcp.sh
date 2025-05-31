#!/bin/bash

# Simple GCP Deployment with minimal configuration

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Simple GCP Deployment${NC}"

# Check if we should use simple backend or full
USE_SIMPLE=true
if [ "$1" == "--full" ]; then
    USE_SIMPLE=false
    echo -e "${YELLOW}Using full backend with 48k variables${NC}"
else
    echo -e "${YELLOW}Using simple backend for faster deployment${NC}"
fi

# Always use GCP-optimized backend for deployment
cat > main.py << 'EOF'
"""
Google App Engine entry point - GCP Optimized Backend
"""
from backend_gcp import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
EOF

# Create a minimal app.yaml
echo -e "${YELLOW}Creating minimal app.yaml...${NC}"
cat > app_minimal.yaml << 'EOF'
runtime: python311

# Use default instance class for now
instance_class: F1

# Basic scaling
automatic_scaling:
  min_instances: 1
  max_instances: 3

# Environment variables
env_variables:
  FLASK_ENV: "production"
  GAE_ENV: "standard"

# Simple handlers
handlers:
# Serve React build static files
- url: /static
  static_dir: audience-manager/build/static
  
# Serve frontend index
- url: /
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html

# API and backend routes
- url: /.*
  script: auto
EOF

# Deploy with minimal configuration
echo -e "${YELLOW}Deploying with minimal configuration...${NC}"
echo -e "${BLUE}This will use less resources and deploy faster${NC}"

gcloud app deploy app_minimal.yaml --quiet --stop-previous-version

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    PROJECT_ID=$(gcloud config get-value project)
    echo -e "${BLUE}Your app is available at: https://${PROJECT_ID}.appspot.com${NC}"
    echo -e "${YELLOW}Opening in browser...${NC}"
    gcloud app browse
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Try running the fix script first:${NC}"
    echo "./fix_gcp_deployment.sh"
fi