# GCP Admin Deployment Guide for Audience Manager

## Overview
This guide provides step-by-step instructions for GCP administrators to configure the necessary permissions and settings to enable successful deployment of the Audience Manager application.

## Current Issues
1. Cloud Build service account lacks permissions to write logs and push to Artifact Registry
2. Organization policy blocks public access (allUsers) to Cloud Run services
3. Build processes are failing due to insufficient permissions

## Project Information
- **Project ID**: `feisty-catcher-461000-g2`
- **Project Number**: `593977832320`
- **Default Region**: `northamerica-northeast1`
- **Cloud Build Service Account**: `593977832320-compute@developer.gserviceaccount.com`

## Required Permissions Setup

### 1. Grant Cloud Build Service Account Permissions

Run these commands to grant the necessary permissions to the Cloud Build service account:

```bash
# Set project
gcloud config set project feisty-catcher-461000-g2

# Grant Logs Writer permission
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="serviceAccount:593977832320-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter"

# Grant Artifact Registry Writer permission
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="serviceAccount:593977832320-compute@developer.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Grant Cloud Run Developer permission
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="serviceAccount:593977832320-compute@developer.gserviceaccount.com" \
    --role="roles/run.developer"

# Grant Service Account User permission (for Cloud Run deployment)
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="serviceAccount:593977832320-compute@developer.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### 2. Create Artifact Registry Repository

Create the required Docker repository for Cloud Run source deployments:

```bash
# Create repository in northamerica-northeast1
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=northamerica-northeast1 \
    --description="Docker repository for Cloud Run source deployments"

# Create repository in us-central1 (backup region)
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Cloud Run source deployments"
```

### 3. Configure Organization Policy for Public Access

If the application needs to be publicly accessible, you'll need to modify the organization policy:

#### Option A: Create Policy Exception for Specific Services
```bash
# Get current organization ID
ORG_ID=$(gcloud organizations list --format="value(name)")

# Create a policy override for specific services
cat > /tmp/policy.yaml << EOF
constraint: iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
    - "C0abcdefg"  # Your customer ID
    - "allUsers"   # Allow public access
  deniedValues: []
EOF

# Apply policy to the project
gcloud resource-manager org-policies set-policy /tmp/policy.yaml \
    --project=feisty-catcher-461000-g2
```

#### Option B: Use Load Balancer with IAP (Recommended for Production)
Instead of allowing public access directly to Cloud Run, set up a load balancer with Identity-Aware Proxy:

```bash
# This approach maintains security while allowing controlled access
# Documentation: https://cloud.google.com/iap/docs/enabling-cloud-run
```

### 4. Enable Required APIs (if not already enabled)

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    containerregistry.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    --project=feisty-catcher-461000-g2
```

### 5. Verify Service Account Permissions

After granting permissions, verify they're correctly applied:

```bash
# Check Cloud Build service account roles
gcloud projects get-iam-policy feisty-catcher-461000-g2 \
    --flatten="bindings[].members" \
    --filter="bindings.members:593977832320-compute@developer.gserviceaccount.com" \
    --format="table(bindings.role)"
```

Expected output should include:
- roles/artifactregistry.writer
- roles/cloudbuild.builds.builder
- roles/iam.serviceAccountUser
- roles/logging.logWriter
- roles/run.developer

## Deployment Commands

Once permissions are configured, the deployment can proceed with:

### Backend Deployment
```bash
cd audience-manager
./deploy-backend-cloudrun.sh
```

### Frontend Deployment
```bash
cd audience-manager
./deploy-to-gcp.sh
```

### Full Stack Deployment
```bash
cd audience-manager
./deploy-full-gcp.sh
```

## Alternative: Authenticated Access Only

If public access cannot be enabled due to organization policies, deploy with authentication required:

```bash
# Deploy backend (authenticated access only)
gcloud run deploy audience-manager-api \
    --source ./simple-backend \
    --platform managed \
    --region northamerica-northeast1 \
    --no-allow-unauthenticated

# Deploy frontend (authenticated access only)
gcloud run deploy audience-manager \
    --source . \
    --platform managed \
    --region northamerica-northeast1 \
    --no-allow-unauthenticated
```

Users will need to authenticate using:
- Google Cloud Console
- gcloud CLI with: `gcloud auth print-identity-token`
- Service account credentials

## Monitoring and Troubleshooting

### Check Build Logs
```bash
# List recent builds
gcloud builds list --limit=5

# View specific build logs
gcloud builds log BUILD_ID
```

### Check Cloud Run Logs
```bash
# Backend logs
gcloud logs read --service=audience-manager-api --limit=50

# Frontend logs
gcloud logs read --service=audience-manager --limit=50
```

### Common Issues and Solutions

1. **"Permission denied" errors in builds**
   - Ensure Cloud Build service account has artifactregistry.writer role
   - Check that Artifact Registry API is enabled

2. **"FAILED_PRECONDITION" on public access**
   - Organization policy is blocking allUsers
   - Use authenticated access or set up load balancer with IAP

3. **Build timeouts**
   - Increase build timeout in cloudbuild.yaml
   - Check for network connectivity issues

## Security Best Practices

1. **Use Secret Manager** for sensitive configuration:
   ```bash
   gcloud secrets create api-key --data-file=api-key.txt
   gcloud secrets add-iam-policy-binding api-key \
       --member="serviceAccount:593977832320-compute@developer.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

2. **Enable VPC Service Controls** for additional security:
   ```bash
   # Create VPC service perimeter around Cloud Run services
   ```

3. **Set up Cloud Armor** for DDoS protection:
   ```bash
   # Configure Cloud Armor security policies
   ```

## Contact Information

For additional support or questions:
- Project Owner: andrew@tobermory.ai
- Documentation: [Audience Manager README](../README.md)
- GCP Support: https://cloud.google.com/support

## Appendix: Full IAM Roles Reference

### Minimum Required Roles for Deployment
- `roles/artifactregistry.writer` - Push images to Artifact Registry
- `roles/cloudbuild.builds.builder` - Run builds
- `roles/logging.logWriter` - Write build logs
- `roles/run.developer` - Deploy to Cloud Run
- `roles/iam.serviceAccountUser` - Act as service account

### Optional Roles for Enhanced Functionality
- `roles/secretmanager.secretAccessor` - Access secrets
- `roles/cloudtrace.agent` - Write trace data
- `roles/monitoring.metricWriter` - Write custom metrics