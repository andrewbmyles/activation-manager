# Deployment Plan: Semantic Variable Picker Enhancement

## Date: 2025-05-28
## Current Status: Production app is functioning at https://tobermory.ai

## Changes to Deploy
1. **Bug Fix**: Added `type="button"` to buttons in VariableSelector.tsx to prevent form submission
2. **Enhancement**: Semantic picker now returns 50 results with pagination (10 per page)

## Pre-Deployment Checklist

### 1. Code Changes Summary
- **Backend** (`main.py`):
  - Line 378: Changed `search_variables(query, 5)` to `search_variables(query, 50)`
  - Line 396-397: Added score normalization
  
- **Frontend** (`audience-manager/src/components/`):
  - `VariableSelector.tsx`: Added `type="button"` to all buttons
  - `EnhancedNLAudienceBuilder.tsx`: Added pagination state and UI

### 2. Testing Status
- ✅ Backend unit tests: 6/6 passing
- ✅ Frontend logic tests: 5/5 passing
- ✅ Manual testing completed locally

## Deployment Plan

### Phase 1: Pre-Deployment Preparation (10 mins)
1. **Create backup of current production code**
   ```bash
   # Create backup directory
   mkdir -p backups/2025-05-28-pre-enhancement
   
   # Backup current main.py
   cp main.py backups/2025-05-28-pre-enhancement/
   
   # Backup frontend components
   cp -r audience-manager/src/components backups/2025-05-28-pre-enhancement/
   ```

2. **Verify current production is working**
   - Check https://tobermory.ai is accessible
   - Test audience builder functionality
   - Verify semantic search is working

### Phase 2: Build and Test Locally (15 mins)
1. **Build frontend with new changes**
   ```bash
   cd audience-manager
   npm run build
   cd ..
   ```

2. **Test backend locally**
   ```bash
   python main.py
   # Test the /api/nl/process endpoint
   ```

3. **Run integration test**
   - Create an audience with semantic search
   - Verify pagination appears with >10 results
   - Test "Show All" functionality
   - Confirm button clicks don't cause redirects

### Phase 3: Deploy to Test Version (15 mins)
1. **Deploy to a test version first**
   ```bash
   # Deploy as version 'test-semantic-v1' without traffic
   gcloud app deploy app_production.yaml \
     --version=test-semantic-v1 \
     --no-promote \
     --project=feisty-catcher-461000-g2
   ```

2. **Test the deployed version**
   ```bash
   # Access test version directly
   https://test-semantic-v1-dot-feisty-catcher-461000-g2.ue.r.appspot.com
   ```

3. **Verify functionality**
   - Create test audience
   - Test semantic search returns more results
   - Verify pagination works
   - Confirm no form submission bugs

### Phase 4: Production Deployment (10 mins)
1. **If test version passes all checks, promote to production**
   ```bash
   # Option A: Gradual traffic migration (recommended)
   gcloud app services set-traffic default \
     --splits=test-semantic-v1=10,production=90 \
     --project=feisty-catcher-461000-g2
   
   # Monitor for 10 minutes, then increase if stable
   gcloud app services set-traffic default \
     --splits=test-semantic-v1=50,production=50 \
     --project=feisty-catcher-461000-g2
   
   # Finally, full migration
   gcloud app services set-traffic default \
     --splits=test-semantic-v1=100 \
     --project=feisty-catcher-461000-g2
   ```

   **OR**

   ```bash
   # Option B: Direct deployment (if confident)
   gcloud app deploy app_production.yaml \
     --version=production-v2 \
     --project=feisty-catcher-461000-g2
   ```

### Phase 5: Post-Deployment Verification (10 mins)
1. **Immediate checks**
   - Access https://tobermory.ai
   - Test login functionality
   - Create a test audience
   - Use semantic search with query like "millennials interested in sustainability"
   - Verify 50 results with pagination
   - Test variable selection doesn't cause redirects

2. **Monitor logs**
   ```bash
   gcloud app logs tail -s default --project=feisty-catcher-461000-g2
   ```

3. **Check error rates**
   ```bash
   gcloud app instances list --project=feisty-catcher-461000-g2
   ```

## Rollback Plan

If any issues occur:

1. **Immediate rollback** (< 2 mins)
   ```bash
   # Revert traffic to previous version
   gcloud app services set-traffic default \
     --splits=production=100 \
     --project=feisty-catcher-461000-g2
   ```

2. **Restore from backup if needed**
   ```bash
   # Copy backup files back
   cp backups/2025-05-28-pre-enhancement/main.py .
   cp -r backups/2025-05-28-pre-enhancement/components/* audience-manager/src/components/
   
   # Rebuild and redeploy
   cd audience-manager && npm run build && cd ..
   gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2
   ```

## Risk Assessment

### Low Risk ✅
- Changes are isolated to specific components
- Backward compatible (existing functionality unchanged)
- Thoroughly tested with unit tests
- Have immediate rollback option

### Potential Issues & Mitigations
1. **Increased API response size**
   - Mitigation: Already tested, 50 variables is still performant
   
2. **Frontend state management**
   - Mitigation: Pagination reduces initial render load
   
3. **Button type changes**
   - Mitigation: Simple HTML fix, low risk of side effects

## Deployment Script

Create `deploy-semantic-enhancement.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Semantic Variable Picker Enhancement"

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p backups/$(date +%Y-%m-%d-%H%M%S)
cp main.py backups/$(date +%Y-%m-%d-%H%M%S)/
cp -r audience-manager/src/components backups/$(date +%Y-%m-%d-%H%M%S)/

# Step 2: Build frontend
echo "🔨 Building frontend..."
cd audience-manager
npm run build
cd ..

# Step 3: Copy Tobermory Web files
echo "📁 Integrating Tobermory Web..."
cp -r tobermory-web/build/* audience-manager/build/

# Step 4: Deploy to test version
echo "🧪 Deploying to test version..."
gcloud app deploy app_production.yaml \
  --version=test-semantic-$(date +%Y%m%d-%H%M%S) \
  --no-promote \
  --quiet \
  --project=feisty-catcher-461000-g2

echo "✅ Test deployment complete!"
echo "🔍 Test at: https://test-semantic-$(date +%Y%m%d-%H%M%S)-dot-feisty-catcher-461000-g2.ue.r.appspot.com"
echo ""
echo "If tests pass, promote with:"
echo "gcloud app versions migrate test-semantic-$(date +%Y%m%d-%H%M%S) --service=default --project=feisty-catcher-461000-g2"
```

## Communication Plan

1. **Before deployment**: "Scheduled maintenance: Updating audience builder with enhanced variable selection (5 mins)"
2. **After deployment**: "Update complete: You can now see more relevant variables with pagination"
3. **If rollback needed**: "We've reverted to the previous version while we investigate an issue"

## Success Criteria

- ✅ Tobermory.ai remains accessible
- ✅ Login functionality works
- ✅ Semantic search returns 50 results
- ✅ Pagination displays correctly
- ✅ Variable selection doesn't cause page redirects
- ✅ No increase in error rates
- ✅ Response times remain under 2 seconds

## Next Steps After Successful Deployment

1. Monitor for 24 hours
2. Gather user feedback on pagination UX
3. Consider adding search/filter within results
4. Update documentation with new features