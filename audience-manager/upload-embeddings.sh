#!/bin/bash

# Upload embeddings to Google Cloud Storage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="audience-manager-embeddings"
LOCAL_EMBEDDINGS_DIR="${1:-./embeddings_final}"

echo -e "${BLUE}=== Uploading Embeddings to GCS ===${NC}"
echo -e "Bucket: ${YELLOW}gs://$BUCKET_NAME${NC}"
echo -e "Local directory: ${YELLOW}$LOCAL_EMBEDDINGS_DIR${NC}"
echo ""

# Check if local directory exists
if [ ! -d "$LOCAL_EMBEDDINGS_DIR" ]; then
    echo -e "${RED}Error: Directory $LOCAL_EMBEDDINGS_DIR not found${NC}"
    echo "Usage: $0 [embeddings_directory]"
    exit 1
fi

# Check for required files
REQUIRED_FILES=("embeddings.h5" "metadata.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$LOCAL_EMBEDDINGS_DIR/$file" ]; then
        echo -e "${RED}Error: Required file $file not found in $LOCAL_EMBEDDINGS_DIR${NC}"
        exit 1
    fi
done

# Optional config file
if [ -f "$LOCAL_EMBEDDINGS_DIR/config.json" ]; then
    echo -e "${GREEN}Found config.json${NC}"
    CONFIG_FILE="$LOCAL_EMBEDDINGS_DIR/config.json"
fi

# Upload files
echo -e "${YELLOW}Uploading embeddings...${NC}"
gsutil -m cp "$LOCAL_EMBEDDINGS_DIR/embeddings.h5" "gs://$BUCKET_NAME/embeddings/"

echo -e "${YELLOW}Uploading metadata...${NC}"
gsutil -m cp "$LOCAL_EMBEDDINGS_DIR/metadata.json" "gs://$BUCKET_NAME/embeddings/"

if [ ! -z "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Uploading config...${NC}"
    gsutil -m cp "$CONFIG_FILE" "gs://$BUCKET_NAME/embeddings/"
fi

# Create a backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo -e "${YELLOW}Creating backup...${NC}"
gsutil -m cp -r "$LOCAL_EMBEDDINGS_DIR" "gs://$BUCKET_NAME/backups/embeddings_$TIMESTAMP/"

# Verify upload
echo -e "${YELLOW}Verifying upload...${NC}"
gsutil ls -l "gs://$BUCKET_NAME/embeddings/"

echo ""
echo -e "${GREEN}=== Upload Complete ===${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Deploy the enhanced backend:"
echo "   export OPENAI_API_KEY=your-key-here"
echo "   ./deploy-embeddings-backend.sh"
echo ""
echo "2. Test the embedding search:"
echo "   curl -X POST https://api.tobermory.ai/api/embeddings/search \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\":\"environmentally conscious millennials\"}'"