# Standard Deployment Workflow

## Overview

All changes must go through staging before production. This ensures quality and prevents breaking the live site.

```
Development → Staging → Testing → Production
     ↓          ↓         ↓          ↓
Local Work   Deploy    Verify    Promote
```

## 🚀 Quick Commands

```bash
# Standard workflow
./deploy.sh -e staging              # 1. Deploy to staging
# ... test in staging ...           # 2. Run tests
./promote-to-prod.sh stg-VERSION    # 3. Promote to production

# Emergency hotfix (use sparingly)
./deploy.sh --skip-tests            # Deploy directly to production
```

## 📋 Step-by-Step Workflow

### 1. Make Your Changes
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# Test locally
npm start (frontend)
python main.py (backend)

# Commit changes
git add .
git commit -m "Add your feature"
```

### 2. Deploy to Staging
```bash
# Always deploy to staging first
./deploy.sh -e staging

# Or use the direct command
./deploy-staging.sh
```

Output will show:
- Staging version: `stg-20240529-123456`
- Staging URL: `https://stg-20240529-123456-dot-feisty-catcher-461000-g2.appspot.com`

### 3. Test in Staging

#### Quick Test (5 minutes)
For minor changes:
- [ ] Open staging URL
- [ ] Login works
- [ ] Changed feature works
- [ ] No console errors
- [ ] Check logs: `gcloud app logs tail --version=stg-VERSION`

#### Full Test (15-30 minutes)
For major changes, use `STAGING_TEST_CHECKLIST.md`:
- [ ] Complete authentication tests
- [ ] Test all Variable Picker features
- [ ] Verify Natural Language interface
- [ ] Check performance
- [ ] Review logs for errors

### 4. Promote to Production
```bash
# When tests pass
./promote-to-prod.sh stg-20240529-123456
```

The script will:
1. Show current production version
2. Display pre-promotion checklist
3. Require confirmation
4. Migrate traffic to staging version
5. Provide rollback command

### 5. Post-Deployment Verification
```bash
# Monitor production
gcloud app logs tail -s default

# Quick health check
curl https://tobermory.ai/api/health

# If issues found - rollback immediately
gcloud app versions migrate PREVIOUS_VERSION
```

## 🎯 Deployment Scenarios

### Regular Feature/Fix
```bash
./deploy.sh -e staging
# Test for 15-30 minutes
./promote-to-prod.sh stg-VERSION
```

### Urgent Hotfix
```bash
./deploy.sh -e staging --skip-tests
# Quick 5-minute test
./promote-to-prod.sh stg-VERSION
```

### Large Release
```bash
./deploy.sh -e staging
# Test for 1-2 hours or overnight
# Get team approval
./promote-to-prod.sh stg-VERSION
```

### Experimental Changes
```bash
./deploy.sh -e staging -v stg-experiment-name
# Test extensively
# May never promote
```

## 📊 Version Management

### Naming Convention
- **Staging**: `stg-YYYYMMDD-HHMMSS`
- **Production**: The promoted staging version

### Cleanup Policy
Keep:
- Last 5 staging versions
- Last 10 production versions
- Any version < 7 days old

Clean up weekly:
```bash
# View old versions
gcloud app versions list --filter="traffic_split=0" --sort-by="~version.createTime" --limit=20

# Delete old staging versions
./cleanup-old-versions.sh
```

## 🚨 Emergency Procedures

### Rollback Production
```bash
# List recent versions
gcloud app versions list --limit=10

# Rollback to previous
gcloud app versions migrate PREVIOUS_GOOD_VERSION

# Or use the saved command from promotion output
```

### Skip Staging (Emergency Only)
```bash
# For critical security fixes only
./deploy.sh -e prod -v hotfix-security

# Document why staging was skipped
echo "Skipped staging due to: [REASON]" >> DEPLOYMENT_LOG.md
```

## 📝 Best Practices

### DO ✅
- Always deploy to staging first
- Test in staging for at least 5 minutes
- Use the checklist for major changes
- Monitor logs after promotion
- Clean up old versions weekly
- Document any deviations

### DON'T ❌
- Skip staging (except emergencies)
- Promote immediately after deploy
- Ignore test failures
- Deploy on Friday afternoon
- Delete recent versions
- Share staging URLs publicly

## 🔄 Continuous Improvement

### Weekly Review
- Review deployment metrics
- Identify failed deployments
- Update checklist based on issues
- Clean up old versions

### Monthly Review
- Analyze deployment patterns
- Optimize deployment times
- Review and update workflow
- Training for new team members

## 📚 Quick Reference Card

```bash
# Deploy to staging
./deploy.sh -e staging

# Check staging URL
echo "https://stg-TIMESTAMP-dot-feisty-catcher-461000-g2.appspot.com"

# Monitor staging logs
gcloud app logs tail --version=stg-TIMESTAMP

# Promote to production
./promote-to-prod.sh stg-TIMESTAMP

# Rollback if needed
gcloud app versions migrate PREVIOUS_VERSION

# View all versions
gcloud app versions list

# Clean up old versions
gcloud app versions delete VERSION1 VERSION2
```

## 🎓 Training Checklist

For new team members:
- [ ] Read this workflow document
- [ ] Deploy to staging (supervised)
- [ ] Complete staging tests
- [ ] Promote to production (supervised)
- [ ] Practice rollback procedure
- [ ] Handle one full deployment solo

## 📈 Success Metrics

Track monthly:
- Deployments through staging: Target 100%
- Failed production deployments: Target < 5%
- Average time in staging: Target 15-30 min
- Rollbacks needed: Target < 2%

---

**Remember**: Staging protects production. A few minutes of testing can save hours of debugging.