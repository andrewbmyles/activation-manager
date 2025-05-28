#!/bin/bash

# Firebase setup script

cd "/Users/myles/Documents/Activation Manager/audience-manager"

echo "=== Setting up Firebase Hosting ==="
echo ""

# First, let's create firebase.json manually
echo "Creating Firebase configuration..."
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

# Create .firebaserc
cat > .firebaserc << EOF
{
  "projects": {
    "default": "feisty-catcher-461000-g2"
  }
}
EOF

echo "Firebase configuration created!"
echo ""

# Build the app
echo "Building the React application..."
npm run build

echo ""
echo "Build complete! Ready to deploy."