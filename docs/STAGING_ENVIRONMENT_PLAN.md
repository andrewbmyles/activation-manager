# Staging Environment Implementation Plan

## Overview

This plan outlines how to set up a staging environment for the Activation Manager that mirrors production and allows easy promotion to production.

## Recommended Approach: GAE Version-Based Staging

### Why This Approach?

1. **Cost-Effective**: Same project, no duplicate resources
2. **Easy Promotion**: One command to promote staging to production
3. **Identical Configuration**: Uses same app.yaml and services
4. **Separate URLs**: Different URLs for testing
5. **Same Data Access**: Access to same data files and GCS buckets

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Google App Engine                    │
│                                                      │
│  ┌─────────────────┐     ┌─────────────────┐      │
│  │   Production    │     │    Staging      │      │
│  │   (100% traffic)│     │   (0% traffic)  │      │
│  │                 │     │                 │      │
│  │ Version: prod-* │     │ Version: stg-*  │      │
│  └─────────────────┘     └─────────────────┘      │
│           │                        │                │
│           ▼                        ▼                │
│  ┌─────────────────────────────────────────┐      │
│  │        Shared Resources                  │      │
│  │  - Data files                           │      │
│  │  - GCS buckets                          │      │
│  │  - Configuration                        │      │
│  └─────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘

URLs:
- Production: https://tobermory.ai
- Staging: https://staging-dot-feisty-catcher-461000-g2.appspot.com
```

## Implementation Steps

### Step 1: Update Deployment Script

Create `deploy-staging.sh`:

```bash
#!/bin/bash
# Deploy to staging environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="feisty-catcher-461000-g2"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STAGING_VERSION="stg-${TIMESTAMP}"

echo -e "${BLUE}🚀 Deploying to Staging Environment${NC}"
echo -e "Version: ${STAGING_VERSION}"
echo ""

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
cd audience-manager
npm run build
cd ..

# Deploy to staging (never promote)
echo -e "${YELLOW}Deploying to staging...${NC}"
gcloud app deploy app_production.yaml \
  --version="${STAGING_VERSION}" \
  --no-promote \
  --quiet \
  --project="${PROJECT_ID}"

echo -e "${GREEN}✅ Staging deployment complete!${NC}"
echo ""
echo -e "${BLUE}Staging URL:${NC}"
echo "https://${STAGING_VERSION}-dot-${PROJECT_ID}.appspot.com"
echo ""
echo -e "${YELLOW}To promote to production:${NC}"
echo "gcloud app versions migrate ${STAGING_VERSION} --project=${PROJECT_ID}"
```

### Step 2: Create Promotion Script

Create `promote-to-prod.sh`:

```bash
#!/bin/bash
# Promote staging version to production

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="feisty-catcher-461000-g2"

# Check if version provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide staging version to promote${NC}"
    echo "Usage: $0 <staging-version>"
    echo ""
    echo "Available staging versions:"
    gcloud app versions list --filter="version.id:stg-*" --project="${PROJECT_ID}"
    exit 1
fi

STAGING_VERSION=$1

# Verify it's a staging version
if [[ ! "$STAGING_VERSION" =~ ^stg- ]]; then
    echo -e "${RED}Error: Version must be a staging version (stg-*)${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Promoting Staging to Production${NC}"
echo -e "Version: ${STAGING_VERSION}"
echo ""

# Show current traffic split
echo -e "${YELLOW}Current traffic allocation:${NC}"
gcloud app services describe default --project="${PROJECT_ID}"

echo ""
read -p "Are you sure you want to promote ${STAGING_VERSION} to production? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Promote staging to production
    gcloud app versions migrate "${STAGING_VERSION}" \
      --service=default \
      --project="${PROJECT_ID}"
    
    echo -e "${GREEN}✅ Successfully promoted ${STAGING_VERSION} to production!${NC}"
    
    # Tag the version as production
    PROD_VERSION="prod-${STAGING_VERSION#stg-}"
    echo -e "${YELLOW}Creating production tag: ${PROD_VERSION}${NC}"
    
    # Optional: Clean up old versions
    echo ""
    echo -e "${YELLOW}Old versions (consider cleaning up):${NC}"
    gcloud app versions list --filter="traffic_split=0" --project="${PROJECT_ID}"
else
    echo -e "${YELLOW}Promotion cancelled${NC}"
fi
```

### Step 3: Update Main Deployment Script

Update `deploy.sh` to support staging:

```bash
# In the select_app_yaml function, add:
staging)
    # Use production config for staging
    APP_YAML="app_production.yaml"
    # Force no-promote for staging
    NO_PROMOTE=true
    ;;
```

### Step 4: Create Testing Checklist

Create `STAGING_TEST_CHECKLIST.md`:

```markdown
# Staging Environment Test Checklist

Before promoting staging to production, verify:

## Functional Tests
- [ ] Login works correctly
- [ ] Variable Picker search returns results
- [ ] Refine functionality works
- [ ] Export (JSON/CSV) works
- [ ] Natural Language interface processes queries
- [ ] All navigation links work

## Performance Tests
- [ ] Page load time < 3 seconds
- [ ] Search response time < 2 seconds
- [ ] No memory leaks (check logs)
- [ ] CPU usage normal

## Visual Tests
- [ ] UI renders correctly
- [ ] Responsive design works
- [ ] No console errors
- [ ] Fonts and images load

## API Tests
- [ ] Health check endpoint responds
- [ ] All API endpoints return expected data
- [ ] Error handling works correctly

## Data Tests
- [ ] Variable data loads correctly
- [ ] Search returns relevant results
- [ ] Data export contains correct information

## Integration Tests
- [ ] Frontend connects to backend
- [ ] CORS headers correct
- [ ] Session management works

## Sign-off
- [ ] QA Approved
- [ ] Stakeholder Review
- [ ] No critical issues in logs
```

### Step 5: DNS Configuration (Optional)

For a cleaner staging URL (staging.tobermory.ai):

1. Add CNAME record:
   ```
   staging.tobermory.ai → ghs.googlehosted.com
   ```

2. Add custom domain in App Engine:
   ```bash
   gcloud app domain-mappings create staging.tobermory.ai \
     --certificate-id=YOUR_CERT_ID
   ```

3. Map to staging versions only

## Workflow

### 1. Deploy to Staging
```bash
./deploy-staging.sh
# or
./deploy.sh -e staging
```

### 2. Test in Staging
- Access staging URL
- Run through test checklist
- Check logs: `gcloud app logs read --version=stg-TIMESTAMP`

### 3. Promote to Production
```bash
./promote-to-prod.sh stg-20240529-123456
```

### 4. Rollback if Needed
```bash
# List previous production versions
gcloud app versions list --filter="version.id:prod-*"

# Rollback
gcloud app versions migrate OLD_PROD_VERSION
```

## Cost Considerations

- **No additional cost** for staging versions (same resources)
- **Storage**: Minimal increase for version artifacts
- **Traffic**: Only when actively testing
- **Recommendation**: Clean up old versions regularly

```bash
# Clean up old staging versions
gcloud app versions delete $(gcloud app versions list \
  --filter="version.id:stg-* AND traffic_split=0" \
  --format="value(id)" \
  --limit=10)
```

## Advanced Options

### Option A: Traffic Splitting (Canary Deployment)
```bash
# Send 10% traffic to staging
gcloud app services set-traffic default \
  --splits=prod-current=90,stg-new=10
```

### Option B: Separate Service
Create `app_staging_service.yaml`:
```yaml
service: staging
runtime: python311
# ... same as production
```

### Option C: Separate Project (Higher Cost)
- Complete isolation
- Separate billing
- Different permissions

## Monitoring

### Staging-Specific Monitoring
```bash
# Watch staging logs
gcloud app logs tail --version=stg-LATEST

# Compare metrics
gcloud app metrics show --version=stg-LATEST
gcloud app metrics show --version=prod-CURRENT
```

## Best Practices

1. **Version Naming Convention**
   - Staging: `stg-YYYYMMDD-HHMMSS`
   - Production: `prod-YYYYMMDD-HHMMSS`

2. **Testing Protocol**
   - Always test in staging first
   - Use checklist for consistency
   - Document any issues found

3. **Promotion Rules**
   - Never promote immediately
   - Minimum 30 minutes testing
   - Require approval for production

4. **Cleanup Policy**
   - Keep last 5 staging versions
   - Keep last 10 production versions
   - Archive older versions

## Summary

This staging setup provides:
- ✅ Identical configuration to production
- ✅ Easy promotion process
- ✅ No additional infrastructure cost
- ✅ Clear separation of environments
- ✅ Simple rollback capability

The version-based approach is the most straightforward and cost-effective solution for your needs.