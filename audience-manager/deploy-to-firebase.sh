#!/bin/bash

# Deploy to Firebase Hosting (Public by default)

echo "=== Deploying to Firebase Hosting ==="
echo ""

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Installing Firebase CLI..."
    npm install -g firebase-tools
fi

# Initialize Firebase
echo "Initializing Firebase project..."
firebase init hosting --project feisty-catcher-461000-g2 << EOF
build
y
n
n
EOF

# Update firebase.json for single-page app
cat > firebase.json << 'EOF'
{
  "hosting": {
    "public": "build",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache"
          }
        ]
      }
    ]
  }
}
EOF

# Build the app
echo "Building the application..."
npm run build

# Deploy to Firebase
echo "Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Your app is now publicly accessible at:"
echo "https://feisty-catcher-461000-g2.web.app"
echo "https://feisty-catcher-461000-g2.firebaseapp.com"
echo ""
echo "To connect your domain:"
echo "1. Go to Firebase Console > Hosting"
echo "2. Click 'Add custom domain'"
echo "3. Follow the instructions to verify and connect tobermory.ai"