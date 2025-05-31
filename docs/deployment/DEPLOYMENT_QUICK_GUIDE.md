# Deployment Quick Reference

## 🚀 Essential Deployment Scripts

After cleanup, we now have only 3 essential deployment scripts:

### 1. `scripts/deploy/deploy-staging.sh`
**Purpose**: Deploy to staging environment for testing
```bash
./scripts/deploy/deploy-staging.sh
```
- Creates version: `stg-YYYYMMDD-HHMMSS`
- Builds frontend optimized for production
- Deploys to Google App Engine (no promotion)

### 2. `scripts/deploy/promote-to-prod.sh`
**Purpose**: Promote tested staging version to production
```bash
./scripts/deploy/promote-to-prod.sh stg-20250530-154449
```
- Routes 100% traffic to specified version
- No code changes or rebuilding
- Instant rollback possible

### 3. `scripts/deploy/deploy-cost-optimized.sh`
**Purpose**: Deploy with cost optimization settings
```bash
./scripts/deploy/deploy-cost-optimized.sh
```
- Uses F1 instance class (lower cost)
- Appropriate for low-traffic periods
- Same functionality, reduced resources

## 📋 Standard Deployment Process

### Step 1: Deploy to Staging
```bash
cd "/Users/myles/Documents/Activation Manager"
./scripts/deploy/deploy-staging.sh
```

### Step 2: Test in Staging
- Wait for deployment to complete (3-5 minutes)
- Test key functionality
- Monitor logs: `gcloud app logs tail --version=stg-VERSION`

### Step 3: Promote to Production
```bash
./scripts/deploy/promote-to-prod.sh stg-VERSION
```

## 🚨 Emergency Procedures

### Quick Rollback
```bash
# Find previous stable version
gcloud app versions list --service=default | grep SERVING

# Route traffic back
gcloud app services set-traffic default --splits=PREVIOUS_VERSION=100
```

### View Production Logs
```bash
gcloud app logs tail --service=default
```

### Check Current Traffic Split
```bash
gcloud app services describe default
```

## 📊 Version Management

### List All Versions
```bash
gcloud app versions list --service=default
```

### Delete Old Versions
```bash
# Keep last 5 versions, delete others
gcloud app versions list --service=default --format="value(version.id)" | tail -n +6 | xargs -I {} gcloud app versions delete {} --quiet
```

## 🔧 Configuration Files

- `app_production.yaml` - Production configuration
- `app_cost_optimized.yaml` - Cost-optimized configuration
- `app.yaml` - Default configuration

## 📝 Notes

- All old deployment scripts archived in `scripts/archive/`
- Test files organized in `tests/` directory structure
- Use staging for all changes before production
- Monitor costs with cost-optimized deployments

---
Last Updated: 2025-05-30