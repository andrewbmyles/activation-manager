#!/bin/bash

# Force SSL certificate check for tobermory.ai

echo "Forcing SSL certificate provisioning check..."

# Trigger certificate check by updating the domain mapping
gcloud beta run domain-mappings update tobermory.ai \
    --region=us-central1 \
    --service=audience-manager \
    --force-override

echo "Checking api.tobermory.ai..."
gcloud beta run domain-mappings update api.tobermory.ai \
    --region=us-central1 \
    --service=audience-manager-api \
    --force-override

echo "Waiting 30 seconds for changes to propagate..."
sleep 30

echo "Current status:"
./monitor-deployment.sh