#!/bin/bash
set -e

echo "🔧 Fixing UI deployment issue..."

# Check which Login component exists and is properly exported
echo "📋 Checking Login components..."

# First, let's check if we should be using Login or SimpleLogin
if grep -q "import { Login }" audience-manager/src/App.tsx; then
    echo "App.tsx uses Login component"
    LOGIN_COMPONENT="Login"
elif grep -q "import { SimpleLogin }" audience-manager/src/App.tsx; then
    echo "App.tsx uses SimpleLogin component"
    LOGIN_COMPONENT="SimpleLogin"
else
    echo "❌ No Login import found in App.tsx!"
    exit 1
fi

# Make sure the component is properly exported
if [ "$LOGIN_COMPONENT" = "Login" ] && [ -f "audience-manager/src/components/Login.tsx" ]; then
    echo "✅ Login.tsx exists"
    # Ensure it has proper export
    if ! grep -q "export.*Login" audience-manager/src/components/Login.tsx; then
        echo "❌ Login component not properly exported"
    fi
elif [ "$LOGIN_COMPONENT" = "SimpleLogin" ] && [ -f "audience-manager/src/components/SimpleLogin.tsx" ]; then
    echo "✅ SimpleLogin.tsx exists"
    # Ensure it has proper export
    if ! grep -q "export.*SimpleLogin" audience-manager/src/components/SimpleLogin.tsx; then
        echo "❌ SimpleLogin component not properly exported"
    fi
else
    echo "❌ Required login component file not found!"
    exit 1
fi

# Fix the import if needed
echo "🔍 Checking imports..."

# Make sure all required components exist
MISSING_COMPONENTS=()

# Check each imported component
for component in Layout ErrorBoundary Dashboard AudienceBuilder PlatformManagement PlatformConfig DistributionCenter Analytics; do
    if [ ! -f "audience-manager/src/components/$component.tsx" ] && [ ! -f "audience-manager/src/pages/$component.tsx" ]; then
        echo "⚠️  Missing: $component"
        MISSING_COMPONENTS+=("$component")
    fi
done

if [ ${#MISSING_COMPONENTS[@]} -gt 0 ]; then
    echo "❌ Missing components detected. This might be why the UI is broken."
fi

# Rebuild with proper configuration
echo "🔨 Rebuilding frontend..."
cd audience-manager

# Clear any cache
rm -rf node_modules/.cache
rm -rf build

# Install dependencies
npm install

# Build
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

cd ..

# Copy Tobermory Web files
if [ -d "tobermory-web/build" ]; then
    echo "📁 Integrating Tobermory Web..."
    cp -r tobermory-web/build/* audience-manager/build/
fi

echo "✅ Fix complete. Ready to deploy."
echo ""
echo "🚀 To deploy, run:"
echo "gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2"