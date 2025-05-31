# Staging Environment Implementation Guide

## Quick Start

### 1. Deploy to Staging
```bash
./deploy-staging.sh
```

This will:
- Build the frontend
- Deploy to a staging version (stg-TIMESTAMP)
- NOT affect production traffic
- Give you a unique staging URL

### 2. Test in Staging
1. Open the staging URL provided
2. Run through `STAGING_TEST_CHECKLIST.md`
3. Monitor logs: `gcloud app logs tail --version=stg-TIMESTAMP`

### 3. Promote to Production
```bash
./promote-to-prod.sh stg-20240529-123456
```

This will:
- Verify the staging version exists
- Show pre-promotion checklist
- Require confirmation
- Migrate 100% traffic to the staging version
- Provide rollback commands

## How It Works

```
Developer → Staging → Testing → Production
    ↓         ↓         ↓          ↓
  Code    stg-VERSION  QA Pass  Live Site
```

### Version Naming Convention
- **Staging**: `stg-YYYYMMDD-HHMMSS`
- **Production**: Currently promoted staging version

### URLs
- **Production**: https://tobermory.ai
- **Staging**: https://stg-TIMESTAMP-dot-feisty-catcher-461000-g2.appspot.com

## Benefits

1. **Zero Downtime**: Instant traffic migration
2. **Easy Rollback**: One command to revert
3. **Cost Effective**: Same infrastructure
4. **Identical Config**: Uses production app.yaml
5. **Real Testing**: Actual GAE environment

## Common Tasks

### View All Versions
```bash
gcloud app versions list
```

### View Staging Versions Only
```bash
gcloud app versions list --filter="version.id:stg-*"
```

### Check Current Production
```bash
gcloud app versions list --filter="traffic_split>0"
```

### Rollback Production
```bash
# Find previous version
gcloud app versions list --filter="traffic_split=0" --limit=5

# Rollback
gcloud app versions migrate OLD_VERSION
```

### Clean Up Old Staging
```bash
# List old staging versions
gcloud app versions list --filter="version.id:stg-* AND traffic_split=0" --limit=10

# Delete them
gcloud app versions delete VERSION1 VERSION2 VERSION3
```

## Advanced Usage

### Deploy Without Building
```bash
./deploy.sh -e staging --skip-build
```

### Deploy Specific Version Name
```bash
./deploy.sh -e staging -v stg-feature-xyz
```

### Traffic Splitting (Canary)
```bash
# 10% to staging, 90% to current
gcloud app services set-traffic default --splits=prod-current=90,stg-new=10
```

## Best Practices

1. **Always Test First**: Never promote without testing
2. **Use Checklist**: Follow STAGING_TEST_CHECKLIST.md
3. **Monitor Logs**: Watch for errors during testing
4. **Document Issues**: Note any problems in staging
5. **Clean Up**: Delete old versions regularly

## Troubleshooting

### Staging Deploy Fails
```bash
# Check auth
gcloud auth list

# Check project
gcloud config get-value project

# Check quota
gcloud app versions list | wc -l
```

### Can't Access Staging URL
- Wait 1-2 minutes for deployment
- Check version status: `gcloud app versions describe stg-VERSION`
- Try incognito mode (cache issues)

### Promotion Fails
- Ensure staging version exists
- Check if you have permission
- Verify no traffic splitting active

## Summary

The staging environment provides a safe, cost-effective way to test changes before production. It uses Google App Engine's built-in versioning system, making it simple to promote good builds and rollback bad ones.

**Key Commands:**
- Deploy: `./deploy-staging.sh`
- Test: Use staging URL + checklist
- Promote: `./promote-to-prod.sh stg-VERSION`
- Rollback: `gcloud app versions migrate OLD_VERSION`