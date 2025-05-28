#!/bin/bash

echo "=== Creating Firebase Hosting Site ==="
echo ""

# First, let's check if Firebase Hosting is enabled
echo "Enabling Firebase Hosting API..."
firebase projects:addfirebase feisty-catcher-461000-g2 2>/dev/null || echo "Project may already have Firebase enabled"

# Create a hosting site
echo ""
echo "Creating hosting site..."
firebase hosting:sites:create audience-manager-site --project feisty-catcher-461000-g2 2>/dev/null || echo "Site may already exist"

# Update firebase.json to use the new site
echo ""
echo "Updating firebase.json with the site name..."
cat > firebase.json << 'EOF'
{
  "hosting": {
    "site": "audience-manager-site",
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
    ]
  }
}
EOF

echo ""
echo "Configuration updated! Now try deploying:"
echo "firebase deploy --only hosting --project feisty-catcher-461000-g2"