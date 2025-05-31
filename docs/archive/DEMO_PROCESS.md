# Demo Preparation Process

## Quick Demo Setup (2-3 minutes before demo)

### 1. Scale Up for Demo Performance
```bash
./prepare-for-demo.sh
```
**What this does:**
- Upgrades to F4_1G instances (maximum performance)
- Keeps 2 instances always warm (instant response)
- Pre-loads embeddings for zero cold-start delays
- Sets aggressive scaling (50% CPU threshold)
- Optimizes caching for fast UI loads

### 2. Warm Up the Application
```bash
./demo-warmup.sh
```
**What this does:**
- Tests all critical endpoints
- Triggers first requests to warm up instances
- Pre-loads embeddings if needed
- Ensures < 2 second first response

### 3. After Demo - Return to Cost Mode
```bash
./return-to-cost-optimized.sh
```
**What this does:**
- Scales back to F2 instances
- Returns to cost-optimized scaling
- Saves ~$200-300/month vs staying in demo mode

## Demo Configuration Details

### Performance Optimizations
- **Instance Class:** F4_1G (vs F2 in cost mode)
- **Always Warm:** 2 instances minimum (vs 0 in cost mode)  
- **Aggressive Scaling:** 50% CPU (vs 75% in cost mode)
- **Pre-loaded Embeddings:** Warmup strategy (vs lazy loading)
- **Enhanced Caching:** 1-day static file cache

### Expected Performance
- **First Request:** < 2 seconds
- **Subsequent Requests:** < 1 second
- **Variable Search:** < 5 seconds
- **Zero Cold Starts:** Always-warm instances

### Cost Impact
- **Demo Mode:** ~$300-500/month
- **Cost-Optimized:** ~$75-150/month
- **Recommendation:** Only use demo mode during actual demos

## Demo Day Checklist

### 30 Minutes Before Demo
- [ ] Run `./prepare-for-demo.sh`
- [ ] Verify deployment success
- [ ] Check application URL is accessible

### 5 Minutes Before Demo
- [ ] Run `./demo-warmup.sh`
- [ ] Test key user flows
- [ ] Verify embeddings are loaded

### During Demo
- [ ] Application should respond instantly
- [ ] No cold start delays
- [ ] Smooth user experience

### After Demo
- [ ] Run `./return-to-cost-optimized.sh`
- [ ] Verify cost-optimized mode is active
- [ ] Monitor costs return to normal

## Emergency Procedures

### If Demo Performance Issues
```bash
# Check current configuration
gcloud app versions list

# Force redeploy demo config
gcloud app deploy app_demo_ready.yaml --promote

# Check instance status
gcloud app instances list
```

### If Demo Fails Completely
```bash
# Emergency rollback to last known good
gcloud app deploy app_production.yaml --promote
```

### Quick Health Check
```bash
curl https://feisty-catcher-461000-g2.nn.r.appspot.com/health
```

## Performance Monitoring During Demo

### Real-time Monitoring
- **GCP Console:** Monitor instance count and CPU
- **Response Times:** Should stay under 2 seconds
- **Error Rates:** Should be near 0%

### Post-Demo Analysis
- Review GCP logs for any issues
- Check total demo mode costs
- Document any performance learnings

## Configuration Comparison

| Mode | Instance | Min Instances | CPU Threshold | Cost/Month | Use Case |
|------|----------|---------------|---------------|------------|----------|
| Cost-Optimized | F2 | 0 | 75% | $75-150 | Daily use |
| Demo-Ready | F4_1G | 2 | 50% | $300-500 | Demos only |
| Ultra-Minimal | F1 | 0 | 80% | $30-75 | Testing |

## Best Practices

1. **Always return to cost-optimized** after demos
2. **Test demo flow** in cost-optimized mode first
3. **Run warmup script** before every demo
4. **Monitor costs** if demo mode is left on accidentally
5. **Keep demo sessions short** to minimize cost impact

## Scripts Summary

- `./prepare-for-demo.sh` - Scale up for maximum performance
- `./demo-warmup.sh` - Warm up application before demo
- `./return-to-cost-optimized.sh` - Return to cost-efficient mode
- `./deploy-cost-optimized.sh` - Deploy cost-optimized config
- `./deploy-minimal-cost.sh` - Deploy ultra-minimal config