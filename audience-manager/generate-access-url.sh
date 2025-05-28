#!/bin/bash

# Generate authenticated access URL

echo "=== Generating Authenticated Access URL ==="
echo ""

# Get identity token
TOKEN=$(gcloud auth print-identity-token)

if [ -z "$TOKEN" ]; then
    echo "Error: Could not generate token. Please run 'gcloud auth login' first."
    exit 1
fi

echo "You can access the application using these methods:"
echo ""
echo "1. Browser Access:"
echo "   - Open Chrome/Firefox"
echo "   - Install ModHeader extension"
echo "   - Add header: Authorization = Bearer $TOKEN"
echo "   - Visit: https://tobermory.ai"
echo ""
echo "2. Direct API Access:"
echo "   curl -H \"Authorization: Bearer $TOKEN\" https://api.tobermory.ai/health"
echo ""
echo "3. Temporary Public Preview URL (valid for 1 hour):"
echo "   Generating preview URL..."

# Create a temporary proxy
gcloud run services proxy audience-manager --region=us-central1 --port=8080 &
PROXY_PID=$!

echo "   Preview will be available at: http://localhost:8080"
echo "   (Press Ctrl+C to stop the preview)"

wait $PROXY_PID