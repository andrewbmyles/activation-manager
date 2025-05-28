# Custom Domain Setup for Audience Manager

## Prerequisites
- A domain name (e.g., audiencemanager.yourdomain.com)
- Access to your domain's DNS settings
- The domain verified in Google Cloud

## Step 1: Verify Domain Ownership in Google Cloud

First, let's verify your domain:

```bash
# Replace YOUR_DOMAIN with your actual domain
gcloud domains verify YOUR_DOMAIN
```

## Step 2: Map Custom Domain to Cloud Run Services

### For Frontend (Main Application):
```bash
gcloud run domain-mappings create \
    --service=audience-manager \
    --domain=YOUR_DOMAIN \
    --region=northamerica-northeast1
```

### For Backend API (Subdomain):
```bash
gcloud run domain-mappings create \
    --service=audience-manager-api \
    --domain=api.YOUR_DOMAIN \
    --region=northamerica-northeast1
```

## Step 3: Configure DNS Records

After running the commands above, you'll receive DNS records to add. They'll look like:

### For Frontend:
- **Type**: A
- **Name**: @ (or blank)
- **Value**: IP addresses provided by Google

- **Type**: AAAA  
- **Name**: @ (or blank)
- **Value**: IPv6 addresses provided by Google

### For API Subdomain:
- **Type**: CNAME
- **Name**: api
- **Value**: ghs.googlehosted.com

## Step 4: Update Frontend Configuration

Update the frontend to use the custom API domain:

```bash
# Update environment variable
echo "REACT_APP_API_URL=https://api.YOUR_DOMAIN" > .env.production

# Rebuild and redeploy frontend
npm run build
gcloud run deploy audience-manager --source . --region=northamerica-northeast1
```

## Step 5: Configure SSL Certificates

Google Cloud Run automatically provisions SSL certificates for custom domains. This process can take up to 24 hours.

## Step 6: Set Up Public Access (Optional)

If you want to make the site publicly accessible:

```bash
# Allow public access to frontend
gcloud run services add-iam-policy-binding audience-manager \
    --region=northamerica-northeast1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# Allow public access to API
gcloud run services add-iam-policy-binding audience-manager-api \
    --region=northamerica-northeast1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

## Example Setup Script

Here's a complete script for setting up a custom domain:

```bash
#!/bin/bash

# Configuration
DOMAIN="audiencemanager.yourdomain.com"
API_DOMAIN="api.audiencemanager.yourdomain.com"
REGION="northamerica-northeast1"

# Verify domain (if not already verified)
echo "Please verify your domain ownership if not already done:"
echo "Visit: https://console.cloud.google.com/apis/credentials/domainverification"
read -p "Press enter when domain is verified..."

# Map frontend domain
echo "Mapping frontend to $DOMAIN..."
gcloud run domain-mappings create \
    --service=audience-manager \
    --domain=$DOMAIN \
    --region=$REGION

# Map API domain
echo "Mapping API to $API_DOMAIN..."
gcloud run domain-mappings create \
    --service=audience-manager-api \
    --domain=$API_DOMAIN \
    --region=$REGION

# Display DNS instructions
echo ""
echo "=== DNS Configuration Required ==="
echo "Add these records to your DNS provider:"
echo ""
gcloud run domain-mappings describe \
    --domain=$DOMAIN \
    --region=$REGION \
    --format="table(metadata.annotations.run.googleapis.com/dns-records[].type,metadata.annotations.run.googleapis.com/dns-records[].name,metadata.annotations.run.googleapis.com/dns-records[].data)"

echo ""
echo "For API subdomain, add:"
echo "Type: CNAME"
echo "Name: api"
echo "Value: ghs.googlehosted.com"
```

## Common DNS Providers Instructions

### Cloudflare:
1. Set SSL/TLS to "Full"
2. Disable "Proxied" (orange cloud) initially
3. Add the records as provided

### GoDaddy:
1. Go to DNS Management
2. Add A records for @ pointing to Google IPs
3. Add CNAME for api pointing to ghs.googlehosted.com

### Namecheap:
1. Go to Advanced DNS
2. Add the records as "A Record" and "CNAME Record"

## Monitoring Setup Progress

Check domain mapping status:
```bash
# Check frontend
gcloud run domain-mappings describe \
    --domain=YOUR_DOMAIN \
    --region=northamerica-northeast1

# Check API
gcloud run domain-mappings describe \
    --domain=api.YOUR_DOMAIN \
    --region=northamerica-northeast1
```

## Troubleshooting

1. **SSL Certificate Pending**: Can take up to 24 hours
2. **DNS Propagation**: Can take 1-48 hours
3. **Access Denied**: Check IAM policies if public access is needed

## After Setup

Your application will be accessible at:
- Frontend: https://YOUR_DOMAIN
- API: https://api.YOUR_DOMAIN

No authentication required if you enabled public access!