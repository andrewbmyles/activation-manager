# GCP Cost Optimization Guide

## Overview

With the frontend timeout increased to 60 seconds, we can significantly reduce backend resource allocation while maintaining reliability. This guide outlines the available cost optimization configurations.

## Configuration Options

### 1. Cost-Optimized (Recommended for Production)
**File:** `app_cost_optimized.yaml`
**Deploy:** `./deploy-cost-optimized.sh`

**Resource Allocation:**
- Instance Class: F2 (reduced from F4)
- Min Instances: 0 (scales to zero when idle)
- Max Instances: 3 (reduced from 10)
- CPU Threshold: 75% (increased from 65%)
- Embeddings: Enabled with lazy loading

**Cost Savings:** ~40-50% reduction
**Use Case:** Production environment with moderate traffic

### 2. Ultra-Minimal Cost (Development/Testing)
**File:** `app_minimal_cost.yaml`
**Deploy:** `./deploy-minimal-cost.sh`

**Resource Allocation:**
- Instance Class: F1 (smallest available)
- Min Instances: 0
- Max Instances: 2
- CPU Threshold: 80%
- Embeddings: DISABLED

**Cost Savings:** ~70-80% reduction
**Use Case:** Development, testing, or when embeddings not needed

### 3. Original Production (High Performance)
**File:** `app_production.yaml`
**Deploy:** `gcloud app deploy app_production.yaml`

**Resource Allocation:**
- Instance Class: F4_1G
- Min Instances: 0
- Max Instances: 2
- Embeddings: Enabled

**Use Case:** High-traffic production with strict performance requirements

## Frontend Timeout Benefits

The increased frontend timeout (60 seconds) enables these optimizations:

1. **Slower Instance Scaling:** Backends can take longer to respond without user-facing timeouts
2. **Higher CPU Thresholds:** Can tolerate higher CPU usage before scaling
3. **Fewer Instances:** Need fewer parallel instances since each can handle longer requests
4. **Relaxed Health Checks:** Can space out monitoring checks to reduce overhead

## Deployment Instructions

### Quick Deploy (Cost-Optimized)
```bash
./deploy-cost-optimized.sh
```

### Quick Deploy (Ultra-Minimal)
```bash
./deploy-minimal-cost.sh
```

### Manual Deploy
```bash
gcloud app deploy app_cost_optimized.yaml
```

## Monitoring and Adjustments

### Key Metrics to Watch
1. **Instance Hours:** Should decrease significantly
2. **Response Times:** Should remain under 60 seconds
3. **Error Rates:** Should stay low even with fewer instances
4. **Cold Start Frequency:** May increase slightly but shouldn't impact UX

### Adjustment Guidelines
- If you see frequent timeouts, increase max_instances
- If response times are too slow, consider F2 → F4 upgrade
- If cold starts are problematic, set min_instances to 1

## Cost Comparison

| Configuration | Instance Class | Max Instances | Est. Monthly Cost* |
|---------------|----------------|---------------|-------------------|
| Original      | F4            | 10            | $150-300         |
| Cost-Optimized| F2            | 3             | $75-150          |
| Ultra-Minimal | F1            | 2             | $30-75           |

*Estimates based on moderate usage. Actual costs depend on traffic patterns.

## Recommended Strategy

1. **Start with Cost-Optimized** for production
2. **Monitor performance** for 1-2 weeks
3. **Adjust if needed:**
   - Increase instances if seeing timeouts
   - Upgrade instance class if consistently slow
   - Consider Ultra-Minimal for low-traffic periods

## Emergency Rollback

If issues arise, quickly rollback to original config:
```bash
gcloud app deploy app_production.yaml
```

## Additional Cost-Saving Tips

1. **Schedule Deployments:** Deploy Ultra-Minimal during off-hours
2. **Use Cloud Scheduler:** Scale down automatically during known low-traffic periods
3. **Monitor GCS Usage:** Embeddings storage costs can add up
4. **Enable Compression:** Already configured in the optimized configs