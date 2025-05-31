#!/bin/bash
set -e

echo "🔧 Fixing build conflict issue..."

# Step 1: Clean everything
echo "🧹 Cleaning build directories..."
rm -rf audience-manager/build
rm -rf tobermory-web/build
rm -rf audience-manager/node_modules/.cache

# Step 2: Build Activation Manager ONLY
echo "🔨 Building Activation Manager..."
cd audience-manager
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Activation Manager built successfully"

# Step 3: Do NOT copy Tobermory Web files - they're conflicting
echo "⚠️  NOT copying Tobermory Web files to avoid conflicts"

cd ..

# Step 4: Verify the build
echo "📋 Verifying build..."
if [ -f "audience-manager/build/index.html" ]; then
    echo "✅ index.html exists"
    
    # Extract the main.js filename from index.html
    MAIN_JS=$(grep -o 'main\.[^"]*\.js' audience-manager/build/index.html | head -1)
    echo "📄 index.html references: $MAIN_JS"
    
    # Check if that file exists
    if [ -f "audience-manager/build/static/js/$MAIN_JS" ]; then
        echo "✅ JavaScript file exists: $MAIN_JS"
    else
        echo "❌ JavaScript file NOT found: $MAIN_JS"
        echo "Available JS files:"
        ls -la audience-manager/build/static/js/
        exit 1
    fi
else
    echo "❌ Build failed - no index.html"
    exit 1
fi

echo ""
echo "✅ Build fixed and ready for deployment"
echo "🚀 Deploy with:"
echo "gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2"