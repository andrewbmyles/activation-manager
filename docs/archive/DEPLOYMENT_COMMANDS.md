# GCP Deployment Commands

Run these commands in order to deploy both applications to Google Cloud Platform.

## Prerequisites
1. Ensure you're logged in with an account that has App Engine Admin permissions
2. If needed, switch to an admin account:
   ```bash
   gcloud auth login
   ```

## Step 1: Set Project
```bash
gcloud config set project activation-manager-20250514
```

## Step 2: Deploy Backend Service
```bash
# Copy backend files to proper location
cp backend_production.py main.py
cp requirements_production.txt requirements.txt

# Deploy backend
gcloud app deploy backend_production.yaml \
    --project=activation-manager-20250514 \
    --quiet \
    --version=backend-$(date +%Y%m%d%H%M%S)
```

## Step 3: Deploy Activation Manager Frontend
```bash
gcloud app deploy app_activation_manager.yaml \
    --project=activation-manager-20250514 \
    --quiet \
    --version=activation-$(date +%Y%m%d%H%M%S)
```

## Step 4: Deploy Tobermory AI Frontend
```bash
gcloud app deploy app_tobermory_final.yaml \
    --project=activation-manager-20250514 \
    --quiet \
    --version=tobermory-$(date +%Y%m%d%H%M%S)
```

## Step 5: Deploy Dispatch Rules
```bash
# Create dispatch.yaml
cat > dispatch.yaml << 'EOF'
dispatch:
  - url: "*/api/*"
    service: activation-backend
  
  - url: "activation.tobermory.ai/*"
    service: activation-manager
  
  - url: "tobermory.ai/*"
    service: default
  
  - url: "*/*"
    service: default
EOF

# Deploy dispatch rules
gcloud app deploy dispatch.yaml --quiet
```

## Step 6: Verify Deployment
```bash
# Check services
gcloud app services list

# Browse to applications
gcloud app browse
gcloud app browse -s activation-manager
gcloud app browse -s activation-backend
```

## Troubleshooting

### If you get permission errors:
1. Check your current account:
   ```bash
   gcloud auth list
   ```

2. Make sure you have the required roles:
   - App Engine Admin
   - Cloud Build Editor
   - Storage Admin

3. You can add roles with:
   ```bash
   gcloud projects add-iam-policy-binding activation-manager-20250514 \
       --member="user:your-email@domain.com" \
       --role="roles/appengine.appAdmin"
   ```

### To view logs:
```bash
gcloud app logs tail -s default
gcloud app logs tail -s activation-manager
gcloud app logs tail -s activation-backend
```

## URLs After Deployment
- Tobermory AI: https://tobermory.ai
- Activation Manager: https://activation.tobermory.ai
- Backend API: https://activation-backend-dot-activation-manager-20250514.uc.r.appspot.com

## Notes
- Password for Activation Manager: demo2024
- The backend service handles all API requests
- Both frontends are static React apps