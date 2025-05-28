#!/bin/bash

# Setup Load Balancer for Public Access

echo "=== Setting up Load Balancer for Public Access ==="
echo ""
echo "This bypasses organization policy restrictions"
echo ""

# Create a backend service
echo "1. Creating backend service..."
gcloud compute backend-services create audience-manager-backend \
    --global \
    --protocol=HTTP \
    --port-name=http \
    --timeout=30s

# Create NEG (Network Endpoint Group) for Cloud Run
echo "2. Creating serverless NEG..."
gcloud compute network-endpoint-groups create audience-manager-neg \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=audience-manager

gcloud compute network-endpoint-groups create audience-manager-api-neg \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=audience-manager-api

# Add NEG to backend service
echo "3. Adding NEG to backend service..."
gcloud compute backend-services add-backend audience-manager-backend \
    --global \
    --network-endpoint-group=audience-manager-neg \
    --network-endpoint-group-region=us-central1

# Create URL map
echo "4. Creating URL map..."
gcloud compute url-maps create audience-manager-lb \
    --default-service=audience-manager-backend

# Create HTTP proxy
echo "5. Creating HTTP proxy..."
gcloud compute target-http-proxies create audience-manager-proxy \
    --url-map=audience-manager-lb

# Create forwarding rule
echo "6. Creating forwarding rule..."
gcloud compute forwarding-rules create audience-manager-forwarding \
    --global \
    --target-http-proxy=audience-manager-proxy \
    --ports=80

echo ""
echo "=== Load Balancer Setup Complete ==="
echo ""
echo "Your application will be available at the Load Balancer IP in about 5 minutes."
echo "To get the IP address:"
echo "gcloud compute forwarding-rules describe audience-manager-forwarding --global --format='value(IPAddress)'"
echo ""
echo "Note: You can point tobermory.ai to this IP address instead of Cloud Run"