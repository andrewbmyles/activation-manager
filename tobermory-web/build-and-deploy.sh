#!/bin/bash

# Build script for Tobermory AI web application

echo "Building Tobermory AI web application..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the React app
echo "Building React app..."
npm run build

# Copy the build to the main audience-manager directory
echo "Copying build files..."
rm -rf ../audience-manager/build
cp -r build ../audience-manager/

# Update the index.html to include auth check
echo "Updating index.html..."
cat > ../audience-manager/build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#34a896" />
    <meta name="description" content="Tobermory AI - Canadian AI Startup" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>Tobermory AI</title>
    <script>
      // Check auth on load
      window.addEventListener('load', function() {
        const isAuthenticated = localStorage.getItem('isAuthenticated');
        if (!isAuthenticated && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      });
    </script>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

echo "Build complete! The application is ready for deployment."
echo ""
echo "To deploy to Google App Engine:"
echo "1. cd .."
echo "2. gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2"