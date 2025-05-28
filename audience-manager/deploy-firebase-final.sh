#!/bin/bash

echo "=== Firebase Deployment ==="
echo ""
echo "Please follow these steps:"
echo ""
echo "1. First, authenticate with Firebase:"
echo "   firebase login"
echo ""
echo "2. Then deploy to Firebase Hosting:"
echo "   firebase deploy --only hosting"
echo ""
echo "The deployment will give you URLs like:"
echo "- https://feisty-catcher-461000-g2.web.app"
echo "- https://feisty-catcher-461000-g2.firebaseapp.com"
echo ""
echo "Let's start the deployment..."
echo ""

# Try to deploy
firebase deploy --only hosting --project feisty-catcher-461000-g2