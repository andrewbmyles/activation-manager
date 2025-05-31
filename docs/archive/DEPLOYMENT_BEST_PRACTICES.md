# Deployment Best Practices - Activation Manager

## Critical Rules to Prevent Build Conflicts

### 1. **NEVER Mix Build Directories**
- **Problem**: Copying Tobermory Web build files into Activation Manager build caused file conflicts
- **Solution**: Keep builds completely separate
- **Rule**: Each app should have its own deployment process

### 2. **Always Clean Build Directories**
```bash
rm -rf audience-manager/build
rm -rf tobermory-web/build
rm -rf audience-manager/node_modules/.cache
```

### 3. **Verify Build Integrity Before Deployment**
- Check that `index.html` references match actual files
- Ensure no duplicate `main.*.js` files exist
- Verify all referenced assets are present

### 4. **Use the Safe Deployment Script**
```bash
./deploy-production-safe.sh
```

This script:
- Creates automatic backups
- Cleans build directories
- Verifies build integrity
- Deploys to test version first
- Only promotes to production after confirmation

## File Structure Best Practices

### Correct Structure:
```
/activation-manager/
├── main.py                    # Backend serving both apps
├── app_production.yaml        # GAE configuration
├── audience-manager/          # Activation Manager frontend
│   ├── src/
│   ├── public/
│   └── build/                # Build output (git ignored)
└── tobermory-web/            # Tobermory Web frontend (separate)
    ├── src/
    ├── public/
    └── build/                # Build output (git ignored)
```

### What NOT to Do:
- ❌ Don't copy tobermory-web/build/* into audience-manager/build/
- ❌ Don't mix static assets from different apps
- ❌ Don't deploy without cleaning builds first
- ❌ Don't skip the test deployment step

## Deployment Checklist

### Before Every Deployment:
1. [ ] Run `git status` to check for uncommitted changes
2. [ ] Clean all build directories
3. [ ] Build fresh from source
4. [ ] Verify build file consistency
5. [ ] Test locally if making significant changes
6. [ ] Deploy to test version first
7. [ ] Verify test version works correctly
8. [ ] Only then promote to production

### After Deployment:
1. [ ] Check production site loads
2. [ ] Verify all pages work
3. [ ] Test critical functionality
4. [ ] Monitor logs for errors
5. [ ] Keep test version for quick rollback

## Quick Commands

### Safe Deployment:
```bash
./deploy-production-safe.sh
```

### Emergency Rollback:
```bash
# List recent versions
gcloud app versions list --project=feisty-catcher-461000-g2

# Rollback to previous version
gcloud app versions migrate [PREVIOUS_VERSION] --service=default --project=feisty-catcher-461000-g2
```

### Check Logs:
```bash
# Live logs
gcloud app logs tail -s default --project=feisty-catcher-461000-g2

# Recent logs
gcloud app logs read --service=default --limit=50 --project=feisty-catcher-461000-g2
```

## Common Issues and Solutions

### Issue: "Dashboard UI is broken"
**Cause**: Mixed build files from different React apps
**Solution**: Clean builds and deploy only Activation Manager

### Issue: "404 errors for static files"
**Cause**: index.html references don't match actual files
**Solution**: Verify build integrity before deployment

### Issue: "Blank pages after deployment"
**Cause**: JavaScript files not loading correctly
**Solution**: Check browser console, verify file paths match

## Architecture Notes

- **main.py** serves both apps but at different routes:
  - `/` → Activation Manager
  - `/tobermory-web/*` → Tobermory Web (if needed)
- Each app should be built independently
- Static files are served from their respective build directories

## Testing Protocol

1. **Local Testing**:
   ```bash
   python main.py
   # Visit http://localhost:8080
   ```

2. **Test Deployment**:
   - Always deploy with `--no-promote` first
   - Test at the version-specific URL
   - Only promote after verification

3. **Production Deployment**:
   - Use the safe deployment script
   - Monitor for 10 minutes after deployment
   - Keep previous version ready for rollback

## Monitoring

- **Health Check**: https://tobermory.ai/api/health
- **Logs**: GCP Console → App Engine → Logs
- **Versions**: GCP Console → App Engine → Versions

## Contact

If deployment issues persist:
1. Check this document first
2. Review recent commits for changes
3. Rollback to last known good version
4. Debug using test deployments