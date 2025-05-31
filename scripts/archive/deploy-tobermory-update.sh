#!/bin/bash

# Deploy updated Tobermory AI with Activation Manager integration

echo "🚀 Deploying to tobermory.ai..."

# Set the correct project
gcloud config set project feisty-catcher-461000-g2

# Build the React apps
echo "📦 Building React applications..."

# Build Activation Manager
cd audience-manager
npm install
npm run build
cd ..

# Build Tobermory Web
cd tobermory-web
npm install
npm run build
cd ..

# Copy Tobermory Web build files to audience-manager/build
echo "🔄 Integrating Tobermory Web into deployment..."
cp -r tobermory-web/build/* audience-manager/build/

# Copy the tobermory logo
cp tobermory-web/tobermorylogo.png audience-manager/build/

# Deploy using the existing production configuration
echo "🚀 Deploying to Google App Engine..."
gcloud app deploy app_tobermory_final.yaml \
    --project=feisty-catcher-461000-g2 \
    --quiet \
    --version=tobermory-$(date +%Y%m%d%H%M%S)

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your application is available at:"
echo "   https://tobermory.ai"
echo ""
echo "📱 Activation Manager:"
echo "   Click on 'Activation Manager' from tobermory.ai"
echo "   Password: demo2024"