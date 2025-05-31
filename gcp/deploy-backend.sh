#!/bin/bash

# GCP Backend Deployment Script
# This script deploys the Python backend to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="audience-manager-backend"
ENABLE_CLOUD_SQL=false
CLOUD_SQL_INSTANCE=""
DATASET_BUCKET=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --enable-cloud-sql)
            ENABLE_CLOUD_SQL=true
            shift
            ;;
        --cloud-sql-instance)
            CLOUD_SQL_INSTANCE="$2"
            shift 2
            ;;
        --dataset-bucket)
            DATASET_BUCKET="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./deploy-backend.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --project            GCP Project ID (required)"
            echo "  --region             GCP Region (default: us-central1)"
            echo "  --enable-cloud-sql   Enable Cloud SQL integration"
            echo "  --cloud-sql-instance Cloud SQL instance connection name"
            echo "  --dataset-bucket     GCS bucket for dataset storage"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Project ID is required${NC}"
    echo "Use --project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${BLUE}=== GCP Backend Deployment ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo ""

# Set the project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
    appengine.googleapis.com \
    cloudbuild.googleapis.com \
    cloudresourcemanager.googleapis.com \
    compute.googleapis.com \
    secretmanager.googleapis.com \
    redis.googleapis.com \
    storage.googleapis.com

# Create App Engine app if it doesn't exist
echo -e "${YELLOW}Checking App Engine...${NC}"
if ! gcloud app describe &>/dev/null; then
    echo -e "${YELLOW}Creating App Engine app...${NC}"
    gcloud app create --region=$REGION
fi

# Create or update secrets
echo -e "${YELLOW}Setting up secrets...${NC}"

# Function to create or update a secret
create_or_update_secret() {
    SECRET_NAME=$1
    SECRET_VALUE=$2
    
    if gcloud secrets describe $SECRET_NAME &>/dev/null; then
        echo "Updating secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=-
    else
        echo "Creating secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=-
    fi
}

# Prompt for secrets if not in environment
if [ -z "$DATABASE_URL" ]; then
    read -p "Enter DATABASE_URL (or press enter to use Redis): " DATABASE_URL
    DATABASE_URL=${DATABASE_URL:-"redis://redis.googleapis.com:6379"}
fi

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -base64 32)
    echo -e "${YELLOW}Generated SECRET_KEY${NC}"
fi

# Create secrets
create_or_update_secret "database-url" "$DATABASE_URL"
create_or_update_secret "secret-key" "$SECRET_KEY"

# Grant App Engine access to secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding secret-key \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Set up Cloud Storage bucket for dataset
if [ -n "$DATASET_BUCKET" ]; then
    echo -e "${YELLOW}Setting up Cloud Storage bucket...${NC}"
    
    # Create bucket if it doesn't exist
    if ! gsutil ls -b gs://$DATASET_BUCKET &>/dev/null; then
        gsutil mb -p $PROJECT_ID -l $REGION gs://$DATASET_BUCKET
    fi
    
    # Upload sample dataset
    if [ -f "data/sample_data.csv" ]; then
        echo -e "${YELLOW}Uploading sample dataset...${NC}"
        gsutil cp data/sample_data.csv gs://$DATASET_BUCKET/
    fi
    
    # Grant App Engine access to bucket
    gsutil iam ch serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com:objectViewer gs://$DATASET_BUCKET
fi

# Set up Redis (Memorystore)
echo -e "${YELLOW}Checking Redis setup...${NC}"
REDIS_INSTANCE="audience-manager-redis"

if ! gcloud redis instances describe $REDIS_INSTANCE --region=$REGION &>/dev/null; then
    echo -e "${YELLOW}Creating Redis instance...${NC}"
    gcloud redis instances create $REDIS_INSTANCE \
        --size=1 \
        --region=$REGION \
        --redis-version=redis_6_x \
        --tier=basic
fi

# Get Redis host
REDIS_HOST=$(gcloud redis instances describe $REDIS_INSTANCE --region=$REGION --format="value(host)")
echo -e "${GREEN}Redis host: $REDIS_HOST${NC}"

# Update app.yaml with environment variables
echo -e "${YELLOW}Updating app.yaml configuration...${NC}"
cat > gcp/app.yaml << EOF
runtime: python311
instance_class: F2

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
  min_pending_latency: 30ms
  max_pending_latency: automatic
  max_concurrent_requests: 50

env_variables:
  FLASK_ENV: "production"
  REDIS_HOST: "$REDIS_HOST"
  PROJECT_ID: "$PROJECT_ID"
  DATASET_BUCKET: "$DATASET_BUCKET"

handlers:
- url: /api/.*
  script: auto
  secure: always

- url: /health
  script: auto
  secure: always

resources:
  cpu: 2
  memory_gb: 2.3
  disk_size_gb: 10
EOF

# Deploy the backend
echo -e "${YELLOW}Deploying backend to App Engine...${NC}"
cd gcp
gcloud app deploy app.yaml --quiet

# Get the backend URL
BACKEND_URL="https://$PROJECT_ID.appspot.com"
echo -e "${GREEN}Backend deployed successfully!${NC}"
echo -e "${GREEN}Backend URL: $BACKEND_URL${NC}"

# Create a deployment info file for frontend
echo -e "${YELLOW}Creating deployment info for frontend...${NC}"
cat > ../deployment-info.json << EOF
{
  "backend_url": "$BACKEND_URL",
  "project_id": "$PROJECT_ID",
  "region": "$REGION",
  "redis_host": "$REDIS_HOST",
  "dataset_bucket": "$DATASET_BUCKET",
  "deployment_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Update your Vercel frontend with:"
echo "   REACT_APP_API_URL=$BACKEND_URL"
echo ""
echo "2. Test the backend:"
echo "   curl $BACKEND_URL/health"
echo ""
echo "3. View logs:"
echo "   gcloud app logs tail -s default"
echo ""
echo "4. Monitor performance:"
echo "   https://console.cloud.google.com/appengine?project=$PROJECT_ID"