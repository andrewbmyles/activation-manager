# Deployment Guide v1.8.0 - Enhanced Audience Detail Page

## Overview

This guide covers the deployment of version 1.8.0, which introduces the Enhanced Audience Detail Page with semantic variable picker, dynamic scaling controls, and real-time audience calculations.

## 🚀 Quick Deployment

### For Production (Recommended)

```bash
# 1. Prepare for deployment
./deploy-production-safe.sh

# 2. Monitor deployment
./check-deployment-health.sh

# 3. Verify new features
open https://tobermory.ai/audience/demo_audience_123
```

### For Staging/Testing

```bash
# 1. Deploy to staging
./deploy-semantic-enhancement.sh

# 2. Run feature tests
npm test -- --testPathPattern="AudienceDetail|EnhancedAudience"

# 3. Manual testing checklist
./test_semantic_picker_manual.py
```

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (`npm test`)
- [ ] Build successful (`npm run build`)
- [ ] ESLint warnings resolved
- [ ] TypeScript compilation clean

### Feature Validation
- [ ] Semantic variable picker working
- [ ] Real-time calculations accurate
- [ ] Slider controls responsive
- [ ] Toggle switches functional
- [ ] API integration verified

### Data & API
- [ ] Enhanced Variable Picker API deployed
- [ ] Audience data accessible
- [ ] Search endpoints responding
- [ ] Database migrations applied (if any)

### Documentation
- [ ] README updated with v1.8.0 features
- [ ] API documentation current
- [ ] User guide published
- [ ] Deployment notes prepared

## 🛠 Deployment Steps

### Step 1: Backup Current Version

```bash
# Create backup of current deployment
gcloud app versions list
gcloud app versions describe [CURRENT_VERSION] > backup_v1.7.0.yaml

# Backup current build
cp -r build/ backup_build_$(date +%Y%m%d_%H%M%S)/
```

### Step 2: Environment Preparation

```bash
# Set environment variables
export PROJECT_ID="your-project-id"
export VERSION="v1-8-0"
export BRANCH="tobermory-deployment-final"

# Verify GCP authentication
gcloud auth list
gcloud config get-value project
```

### Step 3: Build Process

```bash
# Clean previous builds
rm -rf build/
rm -rf node_modules/.cache/

# Install dependencies
npm install

# Build React application
npm run build

# Verify build integrity
ls -la build/
cat build/index.html | grep -i "semantic\|audience"
```

### Step 4: Deploy to Staging (Optional)

```bash
# Deploy to staging version
gcloud app deploy app.yaml \
  --version=staging-v180 \
  --no-promote \
  --project=$PROJECT_ID

# Test staging version
curl -I https://staging-v180-dot-$PROJECT_ID.appspot.com/audience/test
```

### Step 5: Production Deployment

```bash
# Deploy to production
gcloud app deploy app.yaml \
  --version=$VERSION \
  --promote \
  --project=$PROJECT_ID

# Monitor deployment
gcloud app browse --version=$VERSION
```

### Step 6: Post-Deployment Verification

```bash
# Health checks
curl https://tobermory.ai/health
curl https://tobermory.ai/api/enhanced-variable-picker/stats

# Feature verification
./test_deployment.py --check-audience-detail
./test_semantic_picker_enhancement.py
```

## 🧪 Testing Plan

### Automated Tests

```bash
# Unit tests
npm test -- --testPathPattern="AudienceDetail"

# Integration tests  
npm test -- --testPathPattern="enhancedAudienceIntegration"

# API tests
python test_api_csv_fix.py
python test_semantic_picker_enhancement.py
```

### Manual Testing Checklist

#### Audience Detail Page
- [ ] Navigate to existing audience (`/audience/[id]`)
- [ ] Page loads without errors
- [ ] Audience information displays correctly
- [ ] Back button functions properly

#### Semantic Variable Picker
- [ ] Search box accepts input
- [ ] Results appear as you type
- [ ] Can select variables (up to 3)
- [ ] Variable impact shows correctly
- [ ] Confidence percentages display
- [ ] Remove variables with X button

#### Scaling Controls
- [ ] Experiment slider moves smoothly (0.5-10x)
- [ ] Seed audience slider functional
- [ ] Values update in real-time
- [ ] Display shows current multiplier (e.g., "2.50x")

#### Activation Filters
- [ ] All 5 toggle switches work
- [ ] Filter labels display correctly
- [ ] Impact on audience size visible
- [ ] Switches maintain state

#### Real-time Calculations
- [ ] Audience size updates immediately
- [ ] Math appears correct
- [ ] No negative numbers
- [ ] Numbers format with commas

#### Manual Selection Mode
- [ ] Toggle to manual selection works
- [ ] Original criteria display
- [ ] Can switch back to semantic mode
- [ ] Mode state persists during session

### Performance Testing

```bash
# Load testing
curl -w "@curl-format.txt" -s "https://tobermory.ai/audience/test"

# Search response time
time curl -X POST "https://tobermory.ai/api/enhanced-variable-picker/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "high income millennials", "top_k": 10}'

# Memory usage monitoring
./monitor-memory-usage.sh
```

### Browser Compatibility

Test in multiple browsers:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## 🔧 Configuration Updates

### Environment Variables

Add to production environment:

```bash
# Enhanced features
REACT_APP_ENHANCED_AUDIENCE_ENABLED=true
REACT_APP_SEMANTIC_PICKER_ENABLED=true
REACT_APP_MAX_VARIABLES=3

# API endpoints
REACT_APP_ENHANCED_PICKER_ENDPOINT=/api/enhanced-variable-picker
```

### App Engine Configuration

Update `app.yaml` if needed:

```yaml
runtime: python39
env_variables:
  ENHANCED_AUDIENCE_FEATURES: "true"
  MAX_AUDIENCE_VARIABLES: "3"
  
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
```

## 📊 Monitoring & Alerts

### Key Metrics to Monitor

1. **Page Load Times**
   - Audience detail page < 2 seconds
   - Search response < 500ms
   - Calculation updates < 100ms

2. **Error Rates**
   - API errors < 1%
   - Search failures < 0.5%
   - Page crashes < 0.1%

3. **User Engagement**
   - Variable selection usage
   - Slider interaction rates
   - Filter application frequency

### Monitoring Setup

```bash
# Set up monitoring alerts
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/audience-detail-alerts.yaml

# Log analysis queries
gcloud logging read 'resource.type="gae_app" AND 
  jsonPayload.path=~"/audience/" AND 
  severity>=WARNING'
```

### Dashboard Metrics

Track in Google Analytics or monitoring dashboard:
- Audience detail page views
- Search query volume
- Average session duration on audience pages
- Conversion rate (audience detail → activation)

## 🚨 Rollback Plan

### If Issues Occur

1. **Immediate Rollback**
   ```bash
   # Revert to previous version
   gcloud app services set-traffic default \
     --splits=[PREVIOUS_VERSION]=1.0
   ```

2. **Partial Rollback**
   ```bash
   # Split traffic for gradual rollback
   gcloud app services set-traffic default \
     --splits=[NEW_VERSION]=0.1,[PREVIOUS_VERSION]=0.9
   ```

3. **Emergency Procedures**
   ```bash
   # Complete service restoration
   ./emergency-rollback.sh [PREVIOUS_VERSION]
   ./check-deployment-health.sh
   ```

### Rollback Triggers

Automatically rollback if:
- Error rate > 5% for 5 minutes
- Page load time > 5 seconds average
- API response time > 2 seconds
- User reports of missing functionality

## 🔍 Troubleshooting

### Common Issues

#### 1. Page Won't Load
```bash
# Check logs
gcloud app logs tail --service=default

# Verify build
ls -la build/static/js/
```

#### 2. Search Not Working
```bash
# Test API directly
curl -X POST https://tobermory.ai/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'

# Check backend logs
gcloud app logs read --service=default --filter="enhanced-variable-picker"
```

#### 3. Calculations Incorrect
```bash
# Verify formula in browser console
# Check JavaScript errors in DevTools
# Test calculation logic in isolation
```

#### 4. Slow Performance
```bash
# Check instance scaling
gcloud app instances list

# Monitor resource usage
gcloud app operations describe [OPERATION_ID]
```

### Debug Commands

```bash
# Enable debug mode
export DEBUG=true
export REACT_APP_DEBUG=true

# Verbose logging
gcloud app logs tail --service=default --verbosity=debug

# Network analysis
curl -w "@curl-format.txt" -s https://tobermory.ai/audience/test
```

## 📋 Post-Deployment Tasks

### Immediate (0-2 hours)
- [ ] Verify all features working
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Validate API responses

### Short-term (2-24 hours)
- [ ] Monitor user adoption
- [ ] Collect initial feedback
- [ ] Review analytics data
- [ ] Document any issues

### Medium-term (1-7 days)
- [ ] Analyze usage patterns
- [ ] Optimize performance based on data
- [ ] Plan next iteration improvements
- [ ] Update documentation based on findings

## 📝 Deployment Verification

### Success Criteria

The deployment is considered successful when:

1. **Functional Requirements**
   - ✅ All audience detail pages load correctly
   - ✅ Semantic search returns relevant results
   - ✅ Real-time calculations work accurately
   - ✅ All interactive controls respond properly

2. **Performance Requirements**
   - ✅ Page load time < 2 seconds
   - ✅ Search response time < 500ms
   - ✅ No JavaScript errors in console
   - ✅ Mobile responsiveness verified

3. **Integration Requirements**
   - ✅ API endpoints respond correctly
   - ✅ Database operations successful
   - ✅ No breaking changes to existing features
   - ✅ Backward compatibility maintained

### Verification Commands

```bash
# Full feature test
./test_all_changes.py --comprehensive

# Performance benchmark
./benchmark_audience_features.py

# Integration verification
./verify_api_integration.py
```

## 🎯 Success Metrics

After deployment, track these metrics:

### User Engagement
- **Target**: 85% of users try semantic search
- **Target**: 70% use scaling controls
- **Target**: 90% apply at least one filter

### Performance
- **Target**: <2s page load time
- **Target**: <500ms search response
- **Target**: >99% uptime

### User Satisfaction
- **Target**: <5% support tickets about new features
- **Target**: Positive feedback on enhanced UI
- **Target**: Increased time spent on audience pages

---

**Deployment Complete!** 🚀

The Enhanced Audience Detail Page is now live and ready to transform how users interact with audience data. Monitor the metrics above and gather user feedback for continuous improvement.