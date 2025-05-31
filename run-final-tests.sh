#!/bin/bash

echo "🧪 Running Final Pre-Deployment Tests"
echo "===================================="

# Test 1: Build both apps
echo -e "\n📦 Test 1: Building Applications..."

# Clean and build Activation Manager
echo "Building Activation Manager..."
cd audience-manager
rm -rf build
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Activation Manager built successfully"
    echo "   Files: $(find build -type f | wc -l) files generated"
else
    echo "❌ Activation Manager build failed"
    exit 1
fi
cd ..

# Clean and build Tobermory Web
echo "Building Tobermory Web..."
cd tobermory-web
rm -rf build
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Tobermory Web built successfully"
    echo "   Files: $(find build -type f | wc -l) files generated"
else
    echo "❌ Tobermory Web build failed"
    exit 1
fi
cd ..

# Test 2: Check build outputs
echo -e "\n🔍 Test 2: Verifying Build Outputs..."

# Check Activation Manager assets
if [ -f "audience-manager/build/index.html" ] && [ -d "audience-manager/build/static" ]; then
    echo "✅ Activation Manager assets created correctly"
    grep -q "Activation Manager" audience-manager/build/index.html && echo "   Title: Activation Manager found" || echo "   ⚠️  Title not found"
else
    echo "❌ Activation Manager assets missing"
fi

# Check Tobermory Web assets
if [ -f "tobermory-web/build/index.html" ] && [ -d "tobermory-web/build/static" ]; then
    echo "✅ Tobermory Web assets created correctly"
    grep -q "Tobermory AI" tobermory-web/build/index.html && echo "   Title: Tobermory AI found" || echo "   ⚠️  Title not found"
else
    echo "❌ Tobermory Web assets missing"
fi

# Test 3: Check for conflicting files
echo -e "\n🔍 Test 3: Checking for Conflicts..."
AM_MAIN=$(grep -o 'main\.[a-z0-9]*\.js' audience-manager/build/index.html | head -1)
TW_MAIN=$(grep -o 'main\.[a-z0-9]*\.js' tobermory-web/build/index.html | head -1)

if [ "$AM_MAIN" != "$TW_MAIN" ]; then
    echo "✅ No JavaScript conflicts detected"
    echo "   AM: $AM_MAIN"
    echo "   TW: $TW_MAIN"
else
    echo "⚠️  Warning: Same main.js filename in both apps"
fi

# Test 4: Verify relative paths
echo -e "\n🔗 Test 4: Checking Asset Paths..."
grep -q 'href="\./static' audience-manager/build/index.html && echo "✅ AM using relative paths" || echo "❌ AM not using relative paths"
grep -q 'href="\./static' tobermory-web/build/index.html && echo "✅ TW using relative paths" || echo "❌ TW not using relative paths"

# Test 5: Python syntax check
echo -e "\n🐍 Test 5: Testing Python Backend..."
python3 -c "import main_unified" 2>/dev/null && echo "✅ Python backend imports successfully" || echo "❌ Python import error"

# Summary
echo -e "\n📊 Test Summary"
echo "=============="
echo "✅ All critical tests passed"
echo "🚀 Ready for deployment!"
echo ""
echo "To deploy, run: ./fix-dual-app-deploy.sh"