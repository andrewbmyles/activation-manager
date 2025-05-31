#!/bin/bash

# Deploy both Tobermory AI and Activation Manager to Google Cloud Platform

set -e

echo "🚀 Starting GCP deployment for Tobermory AI and Activation Manager..."

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not logged in to gcloud. Please run: gcloud auth login"
    exit 1
fi

# Set project
PROJECT_ID="activation-manager-20250514"
echo "📋 Using project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Build the React apps first
echo "🔨 Building React applications..."

# Build Activation Manager
echo "Building Activation Manager..."
cd audience-manager
npm install
npm run build
cd ..

# Build Tobermory Web
echo "Building Tobermory Web..."
cd tobermory-web
npm install
npm run build
cd ..

# Deploy backend service
echo "🚀 Deploying backend service..."
gcloud app deploy backend_production.yaml \
    --project=$PROJECT_ID \
    --quiet \
    --version=backend-$(date +%Y%m%d%H%M%S)

# Deploy Activation Manager frontend
echo "🚀 Deploying Activation Manager frontend..."
gcloud app deploy app_activation_manager.yaml \
    --project=$PROJECT_ID \
    --quiet \
    --version=activation-$(date +%Y%m%d%H%M%S)

# Deploy Tobermory AI frontend
echo "🚀 Deploying Tobermory AI frontend..."
gcloud app deploy app_tobermory_final.yaml \
    --project=$PROJECT_ID \
    --quiet \
    --version=tobermory-$(date +%Y%m%d%H%M%S)

# Set up dispatch rules
echo "📝 Creating dispatch.yaml..."
cat > dispatch.yaml << EOF
dispatch:
  - url: "*/api/*"
    service: activation-backend
  
  - url: "activation.tobermory.ai/*"
    service: activation-manager
  
  - url: "tobermory.ai/*"
    service: default
  
  - url: "*/*"
    service: default
EOF

echo "🚦 Deploying dispatch rules..."
gcloud app deploy dispatch.yaml --quiet

# Get the URLs
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your applications are available at:"
echo "   - Tobermory AI: https://tobermory.ai"
echo "   - Activation Manager: https://activation.tobermory.ai"
echo "   - Password for Activation Manager: demo2024"
echo ""
echo "📊 View logs:"
echo "   gcloud app logs tail -s default"
echo "   gcloud app logs tail -s activation-manager"
echo "   gcloud app logs tail -s activation-backend"