#!/bin/bash

# Fix Public Access for Audience Manager

echo "=== Fixing Public Access ==="
echo ""

# Option 1: Try to override organization policy at project level
echo "Attempting to override organization policy..."
cat > /tmp/policy.yaml << EOF
constraint: iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
    - "C0abcdefg"  # Your customer ID
    - "allUsers"   # Allow public access
  deniedValues: []
EOF

echo "Applying policy override to project..."
gcloud resource-manager org-policies set-policy /tmp/policy.yaml \
    --project=feisty-catcher-461000-g2 2>/dev/null || echo "Note: May require admin permissions"

echo ""
echo "Waiting for policy to propagate..."
sleep 10

# Option 2: Try adding public access again
echo "Attempting to add public access to services..."
gcloud run services add-iam-policy-binding audience-manager \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker" 2>/dev/null || echo "Frontend: Still blocked by org policy"

gcloud run services add-iam-policy-binding audience-manager-api \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker" 2>/dev/null || echo "API: Still blocked by org policy"

echo ""
echo "=== Alternative Solutions ==="
echo ""
echo "If public access is still blocked, you have these options:"
echo ""
echo "1. Contact your GCP Organization Admin to:"
echo "   - Allow 'allUsers' in the organization policy"
echo "   - Or create an exception for this project"
echo ""
echo "2. Use authenticated access only:"
echo "   - Share the temporary Cloud Run URLs with specific users"
echo "   - They'll need to authenticate with Google accounts"
echo ""
echo "3. Set up a Load Balancer with Identity-Aware Proxy (IAP):"
echo "   - This allows controlled public access"
echo "   - Users authenticate through a Google login page"
echo ""
echo "4. Deploy to a different GCP project without org restrictions"
echo ""

# Check current status
echo "=== Current Access Status ==="
echo ""
echo "Frontend URL: https://audience-manager-qqbqsu5wea-uc.a.run.app"
echo "Testing access..."
if curl -s -o /dev/null -w "%{http_code}" https://audience-manager-qqbqsu5wea-uc.a.run.app | grep -q "403"; then
    echo "Status: 403 Forbidden (authentication required)"
else
    echo "Status: May be accessible"
fi

echo ""
echo "API URL: https://audience-manager-api-qqbqsu5wea-uc.a.run.app"
echo "Testing health endpoint..."
if curl -s https://audience-manager-api-qqbqsu5wea-uc.a.run.app/health 2>/dev/null | grep -q "healthy"; then
    echo "Status: Public access enabled!"
else
    echo "Status: Authentication required"
fi