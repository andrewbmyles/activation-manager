# Data Persistence Deployment Checklist

## Pre-Deployment Verification

### Code Changes
- [x] Backend persistence endpoints added to `main.py`
- [x] Fixed parquet handlers created (`parquet_handlers_fixed.py`)
- [x] Save button added to `EnhancedNLAudienceBuilder.tsx`
- [x] SavedAudiences page component created
- [x] Route added to `App.tsx`
- [x] Navigation link added to `Layout.tsx`

### Testing
- [x] 19 backend unit tests passing
- [x] Thread safety verified
- [x] User isolation confirmed
- [x] Test files created (`test_persistence_integration.py`, `test_ui_save_button.html`)

### Dependencies
- [ ] Verify `pyarrow==13.0.0` in requirements.txt
- [ ] Check pandas version compatibility

### Files to Deploy
```
main.py (modified)
requirements.txt (add pyarrow)
data_persistence/parquet_handlers_fixed.py (new)
src/components/EnhancedNLAudienceBuilder.tsx (modified)
src/components/Layout.tsx (modified)
src/pages/SavedAudiences.tsx (new)
src/App.tsx (modified)
```

## Deployment Steps

1. **Run deployment script**
   ```bash
   ./deploy-data-persistence.sh
   ```

2. **Test on staging URL**
   - Login functionality
   - Create audience
   - Save audience
   - View saved audiences
   - Archive audience

3. **Promote to production**
   ```bash
   gcloud app services set-traffic default --splits=[VERSION]=100 --project=feisty-catcher-461000-g2
   ```

## Post-Deployment Verification

- [ ] Save button appears after creating segments
- [ ] Clicking Save shows success message
- [ ] Saved Audiences link appears in navigation
- [ ] Saved audiences page loads correctly
- [ ] Audiences display with correct information
- [ ] Archive functionality works
- [ ] Data persists after page refresh

## Rollback Commands

```bash
# Immediate traffic rollback
gcloud app services set-traffic default --splits=production=100 --project=feisty-catcher-461000-g2

# Full code rollback
cp backups/[TIMESTAMP]/main.py .
cd audience-manager && npm run build && cd ..
gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2
```

## Known Limitations

1. Currently using 'demo_user' for all saves (auth integration needed)
2. No pagination on saved audiences page yet
3. Export functionality is placeholder
4. Platform and distribution features not exposed yet

## Next Steps After Deployment

1. Monitor storage usage in App Engine console
2. Check error logs for any persistence failures
3. Gather user feedback on save/load experience
4. Plan authentication integration
5. Consider adding search/filter to saved audiences

## Support Contacts

- Deployment issues: Check App Engine logs
- Feature questions: Review implementation guide
- Rollback needed: Use commands above

---

**Ready to deploy?** Run `./deploy-data-persistence.sh`