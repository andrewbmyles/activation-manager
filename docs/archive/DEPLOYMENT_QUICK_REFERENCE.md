# 🚀 Deployment Quick Reference

## Standard Deploy Process (2 Commands)

```bash
# 1. Deploy to staging
./deploy.sh -e staging

# 2. After testing, promote to production
./promote-to-prod.sh stg-YYYYMMDD-HHMMSS
```

That's it! Staging URL will be shown after deploy.

## Common Scenarios

### Regular Feature
```bash
./deploy.sh -e staging                    # Deploy
# Test for 15-30 minutes
./promote-to-prod.sh stg-VERSION          # Promote
```

### Quick Fix
```bash
./deploy.sh -e staging --skip-tests       # Deploy faster
# Test for 5 minutes
./promote-to-prod.sh stg-VERSION          # Promote
```

### Emergency Hotfix
```bash
./deploy.sh -e prod --skip-tests          # Direct to prod (RARE!)
```

## If Something Goes Wrong

### Rollback Production
```bash
# The promote script shows this command
gcloud app versions migrate PREVIOUS_VERSION
```

### Check Logs
```bash
# Staging logs
gcloud app logs tail --version=stg-VERSION

# Production logs
gcloud app logs tail -s default
```

## URLs

- **Production**: https://tobermory.ai
- **Staging**: https://stg-VERSION-dot-feisty-catcher-461000-g2.appspot.com
- **Health Check**: https://tobermory.ai/api/health

## Version Management

### View Versions
```bash
# All versions
gcloud app versions list

# Just staging
gcloud app versions list --filter="version.id:stg-*"

# Currently serving
gcloud app versions list --filter="traffic_split>0"
```

### Cleanup (Weekly)
```bash
./cleanup-old-versions.sh
```

## Testing Checklist

**Quick Test (5 min)**
- [ ] Login works
- [ ] Search works
- [ ] No errors in console
- [ ] Check logs

**Full Test (15-30 min)**
- Use `STAGING_TEST_CHECKLIST.md`

## Tips

1. **Always stage first** (except true emergencies)
2. **Test at least 5 minutes** in staging
3. **Save rollback command** from promotion output
4. **Clean up weekly** to save resources
5. **Document skipped staging** in emergencies

---

Remember: `staging → test → production` prevents problems!