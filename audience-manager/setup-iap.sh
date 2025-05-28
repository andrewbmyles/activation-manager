#!/bin/bash

# Setup Identity-Aware Proxy for controlled public access

echo "=== Setting up Identity-Aware Proxy ==="
echo ""
echo "This allows public access with Google login"
echo ""

# Enable IAP API
echo "Enabling IAP API..."
gcloud services enable iap.googleapis.com

# Create OAuth consent screen
echo ""
echo "MANUAL STEP REQUIRED:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials/consent"
echo "2. Configure OAuth consent screen:"
echo "   - User Type: External"
echo "   - App name: Audience Manager"
echo "   - User support email: andrew@tobermory.ai"
echo "   - Authorized domains: tobermory.ai"
echo "3. Create OAuth 2.0 Client ID:"
echo "   - Go to Credentials"
echo "   - Create Credentials > OAuth client ID"
echo "   - Application type: Web application"
echo "   - Name: Audience Manager IAP"
echo "   - Authorized redirect URIs: https://tobermory.ai/_gcp_gatekeeper/authenticate"
echo ""
echo "Press Enter when you've completed these steps..."
read

# Get the OAuth client ID
echo "Enter the OAuth Client ID you just created:"
read OAUTH_CLIENT_ID

# Enable IAP for the services
echo "Enabling IAP for frontend..."
gcloud iap web enable --resource-type=backend-services \
    --oauth2-client-id=$OAUTH_CLIENT_ID \
    --service=audience-manager-backend

echo ""
echo "=== IAP Setup Complete ==="
echo "Users can now access tobermory.ai and sign in with their Google accounts"