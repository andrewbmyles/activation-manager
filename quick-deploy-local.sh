#!/bin/bash

# Quick Deploy Script with local gcloud path
GCLOUD_PATH="$HOME/google-cloud-sdk/bin/gcloud"

# Check if gcloud exists at this path
if [ ! -f "$GCLOUD_PATH" ]; then
    echo "Google Cloud SDK not found at $GCLOUD_PATH"
    echo "Please make sure you extracted it to your home directory"
    exit 1
fi

echo "Using gcloud at: $GCLOUD_PATH"
echo ""

# Rest of deployment process
echo "Initialize Google Cloud SDK by running:"
echo "$GCLOUD_PATH init"
echo ""
echo "This will:"
echo "1. Open a browser to log into your Google account"
echo "2. Let you create or select a project"
echo "3. Set your default region (choose us-central1)"
echo ""
echo "Press Enter after running gcloud init..."
read

# Continue with deployment...
echo "Now let's deploy your app!"
echo ""
echo "What's your GCP Project ID? (from gcloud init)"
read -p "> " PROJECT_ID

echo ""
echo "Great! Run these commands:"
echo ""
echo "# Enable required APIs"
echo "$GCLOUD_PATH services enable appengine.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com redis.googleapis.com storage.googleapis.com"
echo ""
echo "# Create App Engine app"
echo "$GCLOUD_PATH app create --region=us-central1"
echo ""
echo "Press Enter after running these commands..."
read

echo ""
echo "Now deploy the backend:"
echo "cd gcp"
echo "$GCLOUD_PATH app deploy app.yaml --quiet"
echo ""
echo "Your backend will be at: https://$PROJECT_ID.appspot.com"