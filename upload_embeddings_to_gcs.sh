#!/bin/bash

echo "📤 Uploading embeddings to Google Cloud Storage..."

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
BUCKET_NAME="activation-manager-data"
LOCAL_EMBEDDINGS_DIR="activation_manager/data/embeddings"

# Create bucket if it doesn't exist
echo "Creating GCS bucket if needed..."
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Set bucket permissions
echo "Setting bucket permissions..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Upload embeddings
echo "Uploading embedding files..."
if [ -f "$LOCAL_EMBEDDINGS_DIR/variable_embeddings_full.npy" ]; then
    gsutil -m cp "$LOCAL_EMBEDDINGS_DIR/variable_embeddings_full.npy" gs://$BUCKET_NAME/embeddings/
    echo "✅ Uploaded variable_embeddings_full.npy"
else
    echo "⚠️  variable_embeddings_full.npy not found"
fi

if [ -f "$LOCAL_EMBEDDINGS_DIR/all_variable_embeddings.parquet" ]; then
    gsutil -m cp "$LOCAL_EMBEDDINGS_DIR/all_variable_embeddings.parquet" gs://$BUCKET_NAME/embeddings/
    echo "✅ Uploaded all_variable_embeddings.parquet"
else
    echo "⚠️  all_variable_embeddings.parquet not found"
fi

# Upload other embedding files
for file in "$LOCAL_EMBEDDINGS_DIR"/*.{npy,parquet,jsonl}; do
    if [ -f "$file" ] && [ $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file") -lt 100000000 ]; then
        filename=$(basename "$file")
        gsutil cp "$file" gs://$BUCKET_NAME/embeddings/
        echo "✅ Uploaded $filename"
    fi
done

echo ""
echo "📥 To download embeddings locally, run:"
echo "gsutil -m cp -r gs://$BUCKET_NAME/embeddings/* $LOCAL_EMBEDDINGS_DIR/"
echo ""
echo "🔗 Public URL for embeddings:"
echo "https://storage.googleapis.com/$BUCKET_NAME/embeddings/"