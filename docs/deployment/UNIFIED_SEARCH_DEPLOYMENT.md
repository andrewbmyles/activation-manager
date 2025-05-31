# Unified Search Deployment Guide

## Overview

This guide covers the deployment and gradual rollout of the unified search implementation.

## Current Status

✅ **Week 2 Complete**: Unified search wrapper implemented
✅ **Week 3 In Progress**: Integration with main.py complete, ready for staging deployment

## Architecture

```
┌─────────────────────────────┐
│   Enhanced Variable Picker   │
│         (main.py)            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│    Search Migration Layer    │  ← Feature flags control routing
│  (0-100% rollout control)    │
└──────┬──────────┴──────────┐
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│   Unified    │      │   Legacy     │
│   Search     │      │   Search     │
└──────────────┘      └──────────────┘
```

## Deployment Steps

### 1. Environment Variables

The unified search is controlled by two environment variables:

- `USE_UNIFIED_SEARCH`: Enable unified search (true/false)
- `UNIFIED_ROLLOUT_PERCENTAGE`: Percentage of traffic to route to unified search (0-100)

### 2. Staging Deployment (0% Rollout)

Deploy with migration framework enabled but 0% traffic:

```bash
# Run the deployment script
./deploy-unified-search-staging.sh

# Or manually deploy with environment variables
gcloud app deploy app_staging_unified.yaml \
    --project=tobermory-ai \
    --version=stg-unified-$(date +%Y%m%d-%H%M%S)
```

### 3. Verify Deployment

Test the migration endpoints:

```bash
# Check migration status
curl https://tobermory-ai.uc.r.appspot.com/api/search/migration/status

# Test routing decision
curl -X POST https://tobermory-ai.uc.r.appspot.com/api/search/migration/test \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "query": "test query"}'
```

### 4. Run Integration Tests

```bash
# Test staging deployment
python test_unified_migration.py staging

# Test local deployment
python test_unified_migration.py
```

## Gradual Rollout Process

### Phase 1: 0% Rollout (Current)
- Migration framework deployed
- All traffic goes to legacy search
- Monitor for any deployment issues

### Phase 2: 5% Rollout
```yaml
env_variables:
  USE_UNIFIED_SEARCH: "true"
  UNIFIED_ROLLOUT_PERCENTAGE: "5"
```

### Phase 3: 25% Rollout
- Monitor performance metrics
- Compare A/B test results
- Check error rates

### Phase 4: 50% Rollout
- Significant traffic on unified search
- Final performance validation

### Phase 5: 100% Rollout
- All traffic to unified search
- Legacy can be removed later

## Monitoring

### Key Metrics to Watch

1. **Response Time**
   - Target: <100ms average
   - Alert if >150ms

2. **Filter Effectiveness**
   - Target: >95% reduction for similar patterns
   - Monitor "Contact with friends" patterns

3. **Error Rates**
   - Target: <1% error rate
   - Monitor fallback usage

### Log Analysis

Look for these log patterns:

```bash
# A/B test results
gcloud app logs read --service=default | grep "AB_TEST_RESULT"

# Migration routing decisions
gcloud app logs read --service=default | grep "Routing to"

# Performance violations
gcloud app logs read --service=default | grep "exceeds baseline"
```

## Rollback Process

If issues arise during rollout:

1. **Immediate Rollback**:
   ```yaml
   UNIFIED_ROLLOUT_PERCENTAGE: "0"
   ```

2. **Deploy rollback**:
   ```bash
   gcloud app deploy app.yaml --version=rollback-$(date +%Y%m%d-%H%M%S)
   ```

## API Endpoints

### Migration Control

- `GET /api/search/migration/status` - Current migration status and metrics
- `POST /api/search/migration/test` - Test routing for specific user/query

### Search Endpoints (unchanged)

- `POST /api/enhanced-variable-picker/search` - Main search endpoint
- `GET /api/enhanced-variable-picker/stats` - Variable statistics

## Testing Checklist

- [ ] Migration status endpoint returns correct rollout percentage
- [ ] Search results maintain <100ms latency
- [ ] Similarity filtering reduces patterns by >95%
- [ ] Error fallback works correctly
- [ ] A/B test logging captures metrics
- [ ] No memory leaks or performance degradation

## Next Steps

1. Deploy to staging with 0% rollout ✅
2. Verify migration framework is working
3. Increase to 5% rollout
4. Monitor metrics for 24 hours
5. Gradually increase based on results