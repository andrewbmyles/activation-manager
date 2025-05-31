# Deployment Plan: Data Persistence Feature

## Date: 2025-05-30
## Current Status: Production app is functioning at https://tobermory.ai
## Feature: Save Audiences, Platforms, and Distributions

## Overview

This deployment adds data persistence functionality to allow users to:
- Save created audiences for future use
- View and manage saved audiences
- Archive audiences they no longer need
- Foundation for platform and distribution management

## Changes to Deploy

### 1. Backend Changes
- **Modified** `main.py`:
  - Added persistence API endpoints (lines 542-650)
  - Imported parquet handlers with fallback error handling
  - Added `/api/audiences` endpoints for CRUD operations

- **Added** `data_persistence/parquet_handlers_fixed.py`:
  - Thread-safe Parquet file storage
  - User-isolated data storage
  - Partitioned by date for scalability

### 2. Frontend Changes
- **Modified** `src/components/EnhancedNLAudienceBuilder.tsx`:
  - Added Save button (lines 1076-1081)
  - Added handleSaveAudience function (lines 566-624)
  - Integrated with persistence API

- **Added** `src/pages/SavedAudiences.tsx`:
  - New page for viewing saved audiences
  - Archive and view functionality
  - Variable display with overflow handling

- **Modified** `src/App.tsx`:
  - Added route for `/saved-audiences`

### 3. Test Coverage
- ✅ Backend: 19/19 unit tests passing
- ✅ Thread safety verified
- ✅ User data isolation confirmed
- ✅ Frontend test structure created

## Pre-Deployment Checklist

- [x] All unit tests passing
- [x] Fixed parquet handlers created and tested
- [x] Frontend components integrated
- [ ] Update requirements.txt with pyarrow dependency
- [ ] Create data persistence directory structure
- [ ] Test full save → list → retrieve flow

## Deployment Steps

### Phase 1: Preparation (10 mins)

1. **Update requirements.txt**
   ```bash
   # Ensure pyarrow is in requirements.txt
   echo "pyarrow==13.0.0" >> requirements.txt
   ```

2. **Create backup**
   ```bash
   # Backup current production files
   mkdir -p backups/$(date +%Y%m%d-%H%M%S)-pre-persistence
   cp main.py backups/$(date +%Y%m%d-%H%M%S)-pre-persistence/
   cp -r src/components backups/$(date +%Y%m%d-%H%M%S)-pre-persistence/
   cp -r src/pages backups/$(date +%Y%m%d-%H%M%S)-pre-persistence/
   ```

3. **Update main.py to use fixed handlers**
   ```bash
   # Update the import in main.py
   sed -i '' 's/from data_persistence.parquet_handlers import/from data_persistence.parquet_handlers_fixed import/g' main.py
   ```

### Phase 2: Local Testing (15 mins)

1. **Test backend locally**
   ```bash
   # Install dependencies
   pip install pyarrow==13.0.0
   
   # Run the app
   python main.py
   ```

2. **Test persistence endpoints**
   ```bash
   # Open test UI in browser
   open test_ui_save_button.html
   
   # Or run Python tests
   python test_persistence_integration.py
   ```

3. **Build and test frontend**
   ```bash
   cd audience-manager
   npm run build
   cd ..
   ```

### Phase 3: Deploy to Test Version (20 mins)

1. **Deploy test version**
   ```bash
   # Deploy without promoting
   gcloud app deploy app_production.yaml \
     --version=test-persistence-v1 \
     --no-promote \
     --project=feisty-catcher-461000-g2
   ```

2. **Test on deployed version**
   ```bash
   # Access test URL
   open https://test-persistence-v1-dot-feisty-catcher-461000-g2.ue.r.appspot.com
   ```

3. **Verify functionality**
   - Create and save an audience
   - Navigate to saved audiences page
   - Verify audience appears in list
   - Test archive functionality
   - Check data persistence directory is created

### Phase 4: Production Deployment (15 mins)

1. **Gradual rollout**
   ```bash
   # Start with 10% traffic
   gcloud app services set-traffic default \
     --splits=test-persistence-v1=10,production=90 \
     --project=feisty-catcher-461000-g2
   
   # Monitor for 10 minutes
   
   # Increase to 50% if stable
   gcloud app services set-traffic default \
     --splits=test-persistence-v1=50,production=50 \
     --project=feisty-catcher-461000-g2
   
   # Full migration
   gcloud app services set-traffic default \
     --splits=test-persistence-v1=100 \
     --project=feisty-catcher-461000-g2
   ```

2. **Monitor deployment**
   ```bash
   # Watch logs
   gcloud app logs tail -s default --project=feisty-catcher-461000-g2
   
   # Check instances
   gcloud app instances list --project=feisty-catcher-461000-g2
   ```

### Phase 5: Post-Deployment Verification (10 mins)

1. **Functional tests**
   - Login to https://tobermory.ai
   - Create a new audience
   - Click "Save Audience" button
   - Navigate to saved audiences (need to add to navigation)
   - Verify audience appears
   - Test archive functionality

2. **Data verification**
   ```bash
   # SSH into instance and check data files
   gcloud app instances ssh [INSTANCE_ID] --service=default --version=test-persistence-v1
   
   # Check persistence directory
   ls -la data/persistence/audiences/
   ```

## Rollback Plan

If issues occur:

1. **Immediate rollback**
   ```bash
   # Revert traffic
   gcloud app services set-traffic default \
     --splits=production=100 \
     --project=feisty-catcher-461000-g2
   ```

2. **Code rollback if needed**
   ```bash
   # Restore from backup
   cp backups/[TIMESTAMP]-pre-persistence/main.py .
   cp -r backups/[TIMESTAMP]-pre-persistence/components/* src/components/
   cp -r backups/[TIMESTAMP]-pre-persistence/pages/* src/pages/
   
   # Rebuild and deploy
   cd audience-manager && npm run build && cd ..
   gcloud app deploy app_production.yaml --project=feisty-catcher-461000-g2
   ```

## Deployment Script

Create `deploy-data-persistence.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Data Persistence Feature"

# Variables
PROJECT_ID="feisty-catcher-461000-g2"
VERSION="persistence-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="backups/$(date +%Y%m%d-%H%M%S)-pre-persistence"

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
cp main.py $BACKUP_DIR/
cp -r src/components $BACKUP_DIR/
cp -r src/pages $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/

# Step 2: Update main.py imports
echo "🔧 Updating imports..."
sed -i '' 's/from data_persistence.parquet_handlers import/from data_persistence.parquet_handlers_fixed import/g' main.py

# Step 3: Ensure pyarrow in requirements
echo "📦 Updating requirements..."
if ! grep -q "pyarrow" requirements.txt; then
    echo "pyarrow==13.0.0" >> requirements.txt
fi

# Step 4: Build frontend
echo "🔨 Building frontend..."
cd audience-manager
npm run build
cd ..

# Step 5: Copy Tobermory Web
echo "📁 Integrating Tobermory Web..."
cp -r tobermory-web/build/* audience-manager/build/

# Step 6: Copy persistence handlers
echo "📂 Copying persistence handlers..."
mkdir -p data_persistence
cp data_persistence/parquet_handlers_fixed.py data_persistence/

# Step 7: Deploy to test
echo "🧪 Deploying to test version..."
gcloud app deploy app_production.yaml \
  --version=$VERSION \
  --no-promote \
  --quiet \
  --project=$PROJECT_ID

echo "✅ Test deployment complete!"
echo "🔍 Test at: https://$VERSION-dot-$PROJECT_ID.ue.r.appspot.com"
echo ""
echo "To promote to production:"
echo "gcloud app services set-traffic default --splits=$VERSION=100 --project=$PROJECT_ID"
```

## Risk Assessment

### Low Risk ✅
- New feature doesn't modify existing functionality
- Data is stored locally per user
- Graceful fallback if persistence fails
- Thoroughly tested with unit tests

### Medium Risk ⚠️
- New dependency (pyarrow) could have compatibility issues
- File I/O operations could impact performance
- Storage growth over time needs monitoring

### Mitigations
- Error handling prevents persistence failures from breaking app
- Thread locks ensure data integrity
- Partitioned storage prevents single file growth
- Can disable persistence by removing handlers

## Success Criteria

- ✅ Save button appears after segment confirmation
- ✅ Audiences save successfully with unique IDs
- ✅ Saved audiences page displays list correctly
- ✅ Archive functionality works
- ✅ User data isolation verified (demo_user only sees their data)
- ✅ No performance degradation
- ✅ No increase in error rates

## Post-Deployment Tasks

1. **Add navigation link** to Layout component for saved audiences
2. **Monitor storage usage** in App Engine
3. **Set up data retention policy** (e.g., auto-archive after 90 days)
4. **Document the feature** for users
5. **Plan BigQuery migration** for production scale

## Communication

- **Before**: "New feature coming: Save and manage your audiences!"
- **During**: "Deploying audience persistence feature (5 mins)"
- **After**: "You can now save audiences! Look for the Save button after creating segments"

## Notes

- Currently using 'demo_user' for all saves (need auth integration)
- Saved audiences page route exists but needs navigation link
- Platform and distribution handlers ready but not exposed yet
- Consider adding export functionality in next iteration