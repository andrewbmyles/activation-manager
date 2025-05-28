#!/bin/bash

# Setup script for embedding infrastructure on GCP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
BUCKET_NAME="audience-manager-embeddings"
REGION="us-central1"

echo -e "${BLUE}=== Setting up Embedding Infrastructure ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Bucket: ${YELLOW}$BUCKET_NAME${NC}"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Create Cloud Storage bucket
echo -e "${YELLOW}Creating Cloud Storage bucket...${NC}"
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo -e "${GREEN}Bucket already exists${NC}"
else
    gsutil mb -p $PROJECT_ID -c standard -l $REGION gs://$BUCKET_NAME
    echo -e "${GREEN}Bucket created${NC}"
fi

# Set bucket permissions (private by default)
echo -e "${YELLOW}Setting bucket permissions...${NC}"
gsutil iam ch serviceAccount:593977832320-compute@developer.gserviceaccount.com:objectViewer gs://$BUCKET_NAME

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
echo "Directory structure will be created when you upload files"

# Create sample structure file
cat > embedding_structure.txt << EOF
gs://$BUCKET_NAME/
├── embeddings/
│   ├── embeddings.h5         # FAISS index and embeddings
│   ├── metadata.json         # Variable metadata
│   └── config.json          # Configuration settings
├── models/
│   └── (reserved for future model storage)
└── backups/
    └── (versioned backups)
EOF

echo -e "${GREEN}Bucket structure:${NC}"
cat embedding_structure.txt

echo ""
echo -e "${GREEN}=== Infrastructure Setup Complete ===${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Generate your embeddings locally"
echo "2. Upload to GCS:"
echo "   gsutil cp embeddings.h5 gs://$BUCKET_NAME/embeddings/"
echo "   gsutil cp metadata.json gs://$BUCKET_NAME/embeddings/"
echo "3. Deploy updated backend service"
echo ""
echo -e "${YELLOW}Test bucket access:${NC}"
echo "gsutil ls gs://$BUCKET_NAME/"