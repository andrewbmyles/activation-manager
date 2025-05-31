# Tobermory.ai Deployment Plan

## Current Status Assessment

### ✅ Working Components
1. **Backend API**: Successfully deployed and healthy at `/health`
   - 48,332 variables loaded
   - API endpoints functional
   - GCP App Engine running smoothly

### ❌ Open Issues

#### Issue 1: Frontend Not Serving (404 Error)
**Problem**: The React frontend is not being served at the root URL
**Root Cause**: App.yaml handlers configuration not properly routing static files
**Impact**: Users cannot access the UI

#### Issue 2: Embeddings Storage
**Problem**: Large embedding files (283MB, 67MB) need cloud storage solution
**Root Cause**: Files too large for git, need GCS integration
**Impact**: Full semantic search capability not available in production

#### Issue 3: Custom Domain Setup
**Problem**: Need to map tobermory.ai domain to App Engine
**Root Cause**: Domain configuration not yet implemented
**Impact**: App only accessible via appspot.com URL

#### Issue 4: Frontend-Backend Integration
**Problem**: Potential CORS issues between frontend and backend
**Root Cause**: Domain mismatch between tobermory.ai and appspot.com
**Impact**: API calls may fail from custom domain

#### Issue 5: SSL Certificate
**Problem**: Need SSL for tobermory.ai domain
**Root Cause**: Custom domain requires SSL configuration
**Impact**: Security warning for users

## Strategic Approach

### Phase 1: Fix Frontend Deployment (Priority: Critical)
**Timeline**: 1-2 hours

1. **Build React Frontend**
   ```bash
   cd audience-manager
   npm install
   npm run build
   ```

2. **Update app.yaml Configuration**
   - Properly configure static file handlers
   - Ensure index.html serves for React Router
   - Fix MIME types for static assets

3. **Deploy Updated Configuration**
   - Test locally first
   - Deploy to App Engine
   - Verify frontend loads

### Phase 2: Set Up Cloud Storage for Embeddings (Priority: High)
**Timeline**: 2-3 hours

1. **Create GCS Bucket**
   ```bash
   gsutil mb -p feisty-catcher-461000-g2 gs://activation-manager-embeddings
   ```

2. **Upload Embeddings**
   - Upload local embedding files to GCS
   - Set appropriate permissions

3. **Update Backend Code**
   - Modify variable_selector.py to load from GCS
   - Add fallback for development
   - Test embedding loading

4. **Configure IAM Permissions**
   - Grant App Engine service account access to bucket
   - Test in production

### Phase 3: Custom Domain Configuration (Priority: High)
**Timeline**: 2-4 hours (includes DNS propagation)

1. **Verify Domain Ownership**
   - Add TXT record to tobermory.ai DNS
   - Verify in Google Search Console

2. **Configure Domain Mapping**
   ```bash
   gcloud app domain-mappings create tobermory.ai
   ```

3. **Update DNS Records**
   - Add A records pointing to Google's IPs
   - Add AAAA records for IPv6
   - Configure CNAME if using subdomain

4. **SSL Certificate Setup**
   - Google automatically provisions SSL
   - Monitor certificate status

### Phase 4: Fix CORS and Integration (Priority: Medium)
**Timeline**: 1 hour

1. **Update CORS Configuration**
   - Add tobermory.ai to allowed origins
   - Update backend CORS settings

2. **Environment Variables**
   - Update REACT_APP_API_URL for production
   - Configure backend URLs

3. **Test End-to-End**
   - Verify API calls work from custom domain
   - Check all features function properly

### Phase 5: Production Optimization (Priority: Low)
**Timeline**: 2-3 hours

1. **Performance Optimization**
   - Enable Cloud CDN for static assets
   - Implement caching strategies
   - Optimize embedding loading

2. **Monitoring Setup**
   - Configure Cloud Monitoring
   - Set up alerts
   - Create dashboards

3. **Backup and Recovery**
   - Document deployment process
   - Create backup procedures
   - Test recovery scenarios

## Implementation Steps

### Step 1: Fix Frontend Build and Deployment

```bash
# 1. Build frontend
cd audience-manager
npm install
npm run build

# 2. Create updated app.yaml
cat > app_tobermory.yaml << 'EOF'
runtime: python311
instance_class: F2

automatic_scaling:
  min_instances: 1
  max_instances: 10

env_variables:
  FLASK_ENV: "production"
  USE_EMBEDDINGS: "true"
  GAE_ENV: "standard"
  GOOGLE_CLOUD_PROJECT: "feisty-catcher-461000-g2"
  GCS_BUCKET: "activation-manager-embeddings"
  FRONTEND_URL: "https://tobermory.ai"

handlers:
# API routes
- url: /api/.*
  script: auto
  secure: always

- url: /health
  script: auto
  secure: always

# Static files
- url: /static
  static_dir: audience-manager/build/static
  secure: always
  expiration: "1h"
  http_headers:
    Access-Control-Allow-Origin: "*"

# Frontend assets
- url: /(.*\.(js|css|png|jpg|jpeg|gif|svg|ico|json|txt|map))$
  static_files: audience-manager/build/\1
  upload: audience-manager/build/.*\.(js|css|png|jpg|jpeg|gif|svg|ico|json|txt|map)$
  secure: always
  http_headers:
    Access-Control-Allow-Origin: "*"

# Serve index.html for all other routes
- url: /.*
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
  secure: always
  http_headers:
    Access-Control-Allow-Origin: "*"
EOF
```

### Step 2: Deploy with Fixed Configuration

```bash
# Deploy to App Engine
gcloud app deploy app_tobermory.yaml --project=feisty-catcher-461000-g2
```

### Step 3: Set Up Embeddings in GCS

```bash
# Create and configure bucket
gsutil mb -p feisty-catcher-461000-g2 gs://activation-manager-embeddings
gsutil iam ch serviceAccount:feisty-catcher-461000-g2@appspot.gserviceaccount.com:objectViewer gs://activation-manager-embeddings

# Upload embeddings
gsutil -m cp activation_manager/data/embeddings/*.npy gs://activation-manager-embeddings/
gsutil -m cp activation_manager/data/embeddings/*.parquet gs://activation-manager-embeddings/
```

### Step 4: Configure Custom Domain

```bash
# Add domain mapping
gcloud app domain-mappings create tobermory.ai --project=feisty-catcher-461000-g2

# Get DNS configuration
gcloud app domain-mappings describe tobermory.ai --project=feisty-catcher-461000-g2
```

## Risk Mitigation

1. **Backup Current Working Deployment**
   - Document current configuration
   - Save working app.yaml
   - Note all environment variables

2. **Test Each Phase Independently**
   - Deploy to staging first if available
   - Test with subset of users
   - Monitor error rates

3. **Rollback Plan**
   - Keep previous versions available
   - Document rollback commands
   - Test rollback procedure

## Success Criteria

- [ ] Frontend loads at https://tobermory.ai
- [ ] All API endpoints functional
- [ ] Variable picker works with full dataset
- [ ] No CORS errors
- [ ] SSL certificate active
- [ ] Page load time < 3 seconds
- [ ] All 48,332 variables searchable
- [ ] Semantic search operational

## Timeline Summary

- **Phase 1**: 1-2 hours (Critical - Frontend)
- **Phase 2**: 2-3 hours (High - Embeddings)
- **Phase 3**: 2-4 hours (High - Domain)
- **Phase 4**: 1 hour (Medium - CORS)
- **Phase 5**: 2-3 hours (Low - Optimization)

**Total Estimated Time**: 8-13 hours of active work
**With DNS Propagation**: 24-48 hours total

## Next Immediate Actions

1. Build the React frontend locally
2. Test the updated app.yaml configuration
3. Deploy the fixed frontend
4. Verify frontend accessibility
5. Proceed with embeddings setup

This plan addresses all identified issues systematically, prioritizing user-facing functionality first, then adding full capabilities, and finally optimizing for production use.