#!/bin/bash

echo "🚀 Deploying Production Version with Embeddings Support"
echo "====================================================="

# Copy the production backend
echo "📝 Setting up production backend..."
cp main_production_gcp.py main.py

# Ensure both apps are built with correct settings
echo "🔨 Verifying builds..."

# Check if builds exist, if not build them
if [ ! -d "audience-manager/build" ]; then
    echo "Building Activation Manager..."
    cd audience-manager
    npm run build
    cd ..
fi

if [ ! -d "tobermory-web/build" ]; then
    echo "Building Tobermory Web..."
    cd tobermory-web
    npm run build
    cd ..
fi

# Deploy to GCP
echo "🚀 Deploying to GCP..."
gcloud app deploy app_tobermory_final.yaml \
    --project=feisty-catcher-461000-g2 \
    --quiet \
    --version=production-$(date +%Y%m%d%H%M%S)

echo "✅ Deployment complete!"
echo ""
echo "🧪 Running post-deployment tests..."
sleep 10

# Test the deployment
echo -e "\n📡 Testing deployment..."
curl -s https://tobermory.ai/health | jq .
echo ""
curl -s https://tobermory.ai/api/embeddings/status | jq .

echo ""
echo "🌐 Access your applications at:"
echo "   Tobermory AI: https://tobermory.ai"
echo "   Activation Manager: https://tobermory.ai/activation-manager"
echo "   Password: demo2024"