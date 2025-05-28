#!/bin/bash

# Simple script to open your Audience Manager app with authentication

echo "Opening Audience Manager..."
echo ""
echo "You'll need to sign in with your Google account (andrew@tobermory.ai)"
echo ""

# Get the URLs
FRONTEND_URL="https://audience-manager-593977832320.northamerica-northeast1.run.app"
API_URL="https://audience-manager-api-593977832320.northamerica-northeast1.run.app"

echo "Frontend URL: $FRONTEND_URL"
echo "API URL: $API_URL"
echo ""

# Open in default browser
echo "Opening in your default browser..."
open "$FRONTEND_URL"

echo ""
echo "If the browser didn't open, manually visit:"
echo "$FRONTEND_URL"
echo ""
echo "To test the API directly:"
echo "curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" $API_URL/health"