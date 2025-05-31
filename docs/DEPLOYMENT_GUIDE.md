# Activation Manager Deployment Guide

## Prerequisites

1. **Google Cloud Platform Account**
   - Project created and configured
   - Billing enabled
   - App Engine enabled

2. **Local Development Tools**
   - Node.js 16+ and npm
   - Python 3.11+
   - Google Cloud SDK (`gcloud`)

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Quick Deployment

For a standard deployment to production:

```bash
# 1. Build frontend
cd audience-manager
npm install
npm run build
cd ..

# 2. Deploy to Google App Engine
gcloud app deploy app_production.yaml --quiet
```

## Detailed Deployment Steps

### 1. Environment Setup

```bash
# Clone repository
git clone [repository-url]
cd activation-manager

# Install dependencies
cd audience-manager
npm install
cd ..
pip install -r requirements.txt
```

### 2. Configuration

**Update `app_production.yaml`:**
```yaml
env_variables:
  GOOGLE_CLOUD_PROJECT: "your-project-id"
  GCS_BUCKET: "your-embeddings-bucket"  # Optional
```

### 3. Build Frontend

```bash
cd audience-manager
npm run build

# Verify build
ls -la build/
# Should see: index.html, static/, etc.
```

### 4. Deploy to Google App Engine

```bash
# Deploy with specific version name
gcloud app deploy app_production.yaml \
  --version="v1-0-0" \
  --promote \
  --quiet

# Deploy without promoting (staging)
gcloud app deploy app_production.yaml \
  --version="staging-$(date +%Y%m%d-%H%M%S)" \
  --no-promote
```

### 5. Verify Deployment

```bash
# View application
gcloud app browse

# Check logs
gcloud app logs tail -s default

# Check specific version
gcloud app versions list
```

## Configuration Files

### app_production.yaml
```yaml
runtime: python311
instance_class: F4

automatic_scaling:
  min_instances: 1
  max_instances: 10

handlers:
- url: /static
  static_dir: audience-manager/build/static
- url: /api/.*
  script: auto
- url: /.*
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
```

### .gcloudignore
```
node_modules/
venv/
*.pyc
__pycache__/
.git/
.env
*.log
tests/
docs/
```

## Environment-Specific Deployments

### Development
```bash
# Local development
cd audience-manager && npm start &
python main.py
```

### Staging
```bash
gcloud app deploy app_staging.yaml --version="staging-latest"
```

### Production
```bash
gcloud app deploy app_production.yaml --version="prod-$(date +%Y%m%d)"
```

## Data Files

Ensure data files are included:
- `data/Full_Variable_List_2022_CAN.csv` - Required
- `data/variables_2022_can.parquet` - Optional (faster)

## Rollback Procedures

```bash
# List versions
gcloud app versions list

# Rollback to previous version
gcloud app versions migrate OLD_VERSION

# Or use traffic splitting
gcloud app services set-traffic default \
  --splits=OLD_VERSION=1
```

## Monitoring

### Health Checks
- Production: `https://your-app.appspot.com/api/health`
- Embeddings: `https://your-app.appspot.com/api/embeddings-status`

### Logs
```bash
# Stream logs
gcloud app logs tail -s default

# Read recent logs
gcloud app logs read --limit=50

# Filter logs
gcloud app logs read --logs=request_log
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure all packages in requirements.txt
   pip freeze > requirements.txt
   ```

2. **Build Failures**
   ```bash
   # Clear cache and rebuild
   rm -rf audience-manager/build
   rm -rf audience-manager/node_modules
   cd audience-manager && npm install && npm run build
   ```

3. **502 Bad Gateway**
   - Check logs for startup errors
   - Verify instance class has enough memory
   - Check for missing dependencies

4. **Slow Performance**
   - Upgrade instance class to F4_HIGHMEM
   - Enable warmup requests
   - Check for large file operations

### Debug Commands

```bash
# SSH into instance (if enabled)
gcloud app instances ssh INSTANCE_ID --service=default

# Describe service
gcloud app services describe default

# View instance details
gcloud app instances list
```

## Cost Optimization

1. **Instance Configuration**
   - Use F2 for low traffic
   - F4 for production loads
   - Set appropriate max_instances

2. **Static Files**
   - Serve from CDN if possible
   - Set appropriate cache headers

3. **Monitoring**
   ```bash
   # View billing
   gcloud billing accounts list
   gcloud app services list
   ```

## Security Best Practices

1. **Environment Variables**
   - Never commit secrets
   - Use Secret Manager for sensitive data

2. **Access Control**
   - Enable IAP if needed
   - Restrict deployment permissions

3. **Updates**
   - Keep dependencies updated
   - Regular security scans

## Backup and Recovery

### Backup Data
```bash
# Download data files
gsutil cp gs://your-bucket/data/* ./backup/
```

### Backup Code
```bash
# Tag release
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
```

## CI/CD Pipeline (Optional)

### GitHub Actions Example
```yaml
name: Deploy to GAE
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: google-github-actions/setup-gcloud@v0
    - run: |
        cd audience-manager && npm install && npm run build
        gcloud app deploy app_production.yaml --quiet
```

## Post-Deployment Checklist

- [ ] Application loads correctly
- [ ] Login works
- [ ] Variable search returns results
- [ ] Refine functionality works
- [ ] Export works (JSON/CSV)
- [ ] All navigation links work
- [ ] Console has no errors
- [ ] Performance is acceptable
- [ ] Logs show no errors