#!/bin/bash

# Deploy Enhanced Backend with Embedding Support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
REGION="us-central1"
SERVICE_NAME="audience-manager-api"
BUCKET_NAME="audience-manager-embeddings"

echo -e "${BLUE}=== Deploying Enhanced Backend with Embeddings ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo -e "Service: ${YELLOW}$SERVICE_NAME${NC}"
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY environment variable not set${NC}"
    echo "Please set: export OPENAI_API_KEY=your-key-here"
    exit 1
fi

# First, run the infrastructure setup if needed
echo -e "${YELLOW}Checking infrastructure...${NC}"
if ! gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo -e "${YELLOW}Running infrastructure setup...${NC}"
    chmod +x setup-embeddings-infrastructure.sh
    ./setup-embeddings-infrastructure.sh
fi

# Check if embeddings exist in bucket
echo -e "${YELLOW}Checking for embeddings in GCS...${NC}"
if ! gsutil ls gs://$BUCKET_NAME/embeddings/embeddings.h5 &>/dev/null; then
    echo -e "${YELLOW}Warning: No embeddings found in GCS${NC}"
    echo "Please upload your embeddings:"
    echo "  gsutil cp embeddings.h5 gs://$BUCKET_NAME/embeddings/"
    echo "  gsutil cp metadata.json gs://$BUCKET_NAME/embeddings/"
    echo ""
    read -p "Continue deployment anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy the enhanced backend
echo -e "${YELLOW}Deploying enhanced backend...${NC}"
cd enhanced-backend

# Generate a secure session key
SECRET_KEY=$(openssl rand -hex 32)

# Deploy with increased resources for embeddings
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --set-env-vars "SECRET_KEY=$SECRET_KEY,OPENAI_API_KEY=$OPENAI_API_KEY" \
    --service-account "593977832320-compute@developer.gserviceaccount.com"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

cd ..

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}Test endpoints:${NC}"
echo "# Health check"
echo "curl $SERVICE_URL/health"
echo ""
echo "# Check embedding status (requires auth)"
echo "curl -X POST $SERVICE_URL/api/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"andrew@tobermory.ai\",\"password\":\"admin\"}' -c cookies.txt"
echo "curl $SERVICE_URL/api/embeddings/status -b cookies.txt"
echo ""
echo -e "${YELLOW}Note:${NC} The service will use embeddings if available in GCS, otherwise fallback to default behavior"