# Enhanced Deployment Guide

## Overview

This guide covers deploying the Activation Manager with enhanced semantic search capabilities, including the new Parquet data format and 50-result search functionality.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Python 3.9+** installed locally
3. **Node.js 16+** for building frontend
4. **Google Cloud SDK** installed and configured
5. **~5GB free space** for data and dependencies

## Data Files Required

Ensure these files are present before deployment:

```
data/
├── variables_2022_can.parquet          # 49,323 variables (3MB)
├── Full_Variable_List_2022_CAN.csv     # Fallback CSV (15MB)
└── embeddings/
    ├── variable_embeddings_full.npy    # Pre-computed embeddings
    └── variable_ids_full.json          # Variable ID mapping
```

## Environment Variables

Create a `.env` file or set these in App Engine:

```bash
# Required for semantic search
OPENAI_API_KEY=your-openai-api-key

# Optional configurations
SEARCH_DEFAULT_TOP_K=50
HYBRID_WEIGHT_SEMANTIC=0.7
HYBRID_WEIGHT_KEYWORD=0.3
USE_PARQUET=true
```

## Deployment Steps

### 1. Prepare Data Files

```bash
# Verify parquet file
python -c "import pandas as pd; df=pd.read_parquet('data/variables_2022_can.parquet'); print(f'Loaded {len(df)} variables')"

# Upload to Google Cloud Storage (recommended for production)
gsutil mb gs://your-bucket-name-variables
gsutil cp data/variables_2022_can.parquet gs://your-bucket-name-variables/
gsutil cp -r data/embeddings gs://your-bucket-name-variables/
```

### 2. Update app.yaml

Ensure your `app.yaml` includes:

```yaml
runtime: python39
instance_class: F4  # Recommended for enhanced search
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.65

env_variables:
  USE_PARQUET: "true"
  SEARCH_DEFAULT_TOP_K: "50"

handlers:
- url: /static
  static_dir: audience-manager/build/static
- url: /api/.*
  script: auto
- url: /.*
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
```

### 3. Build Frontend with Enhanced Features

```bash
cd audience-manager
npm install
npm run build

# Verify build includes enhanced components
ls -la build/static/js/
```

### 4. Test Locally

```bash
# Test enhanced search
python test_enhanced_semantic_search.py

# Test parquet loading
python test_parquet_loading.py

# Run Flask app locally
python main.py
```

### 5. Deploy to Google App Engine

```bash
# Deploy with enhanced features
gcloud app deploy app.yaml \
  --project=your-project-id \
  --version=enhanced-v1 \
  --no-promote

# Test the deployment
curl https://enhanced-v1-dot-your-project-id.appspot.com/api/enhanced-variable-picker/stats

# If successful, promote to production
gcloud app versions migrate enhanced-v1 \
  --service=default \
  --project=your-project-id
```

## Performance Optimization

### 1. Enable Memcache for Caching

```yaml
# In app.yaml
env_variables:
  USE_MEMCACHE: "true"
  CACHE_TTL: "3600"
```

### 2. Configure Instance Scaling

For high-traffic applications:

```yaml
automatic_scaling:
  min_instances: 2
  max_instances: 20
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.7
  max_concurrent_requests: 80
```

### 3. Use Cloud CDN for Static Assets

```bash
# Enable Cloud CDN
gcloud compute backend-services update your-backend-service \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC
```

## Monitoring and Logging

### 1. Set Up Monitoring

```bash
# Enable monitoring APIs
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Create alerts for high latency
gcloud alpha monitoring policies create \
  --notification-channels=your-channel-id \
  --display-name="High Search Latency" \
  --condition-threshold-value=1000 \
  --condition-threshold-duration=60s
```

### 2. View Logs

```bash
# View application logs
gcloud app logs read --service=default --limit=50

# View specific search logs
gcloud logging read "resource.type=gae_app AND textPayload:enhanced_search" \
  --limit=20 \
  --format=json
```

### 3. Performance Metrics

Monitor these key metrics:
- **Search Latency**: Should be <200ms for 50 results
- **Memory Usage**: Should stay under 512MB
- **CPU Usage**: Should average <50%
- **Error Rate**: Should be <0.1%

## Troubleshooting

### Issue: Slow Search Performance

**Symptoms**: Searches take >500ms

**Solutions**:
1. Verify Parquet file is being used:
   ```python
   check logs for "Loaded X variables from Parquet"
   ```
2. Check instance class (F4 or higher recommended)
3. Enable caching if not already enabled

### Issue: Out of Memory Errors

**Symptoms**: 500 errors, "Exceeded memory limit"

**Solutions**:
1. Increase instance class to F4_1G
2. Reduce FAISS index size:
   ```python
   # In enhanced_semantic_search.py
   self.faiss_index = faiss.IndexIVFFlat(n_centroids, self.embedding_dim)
   ```

### Issue: Embeddings Not Loading

**Symptoms**: Only keyword search working

**Solutions**:
1. Verify embeddings file exists and is accessible
2. Check OPENAI_API_KEY is set correctly
3. Review logs for embedding loading errors

### Issue: Wrong Number of Results

**Symptoms**: Getting 10 results instead of 50

**Solutions**:
1. Check SEARCH_DEFAULT_TOP_K environment variable
2. Verify using enhanced API endpoint
3. Check frontend is passing correct top_k parameter

## Rollback Procedure

If issues occur after deployment:

```bash
# List versions
gcloud app versions list

# Rollback to previous version
gcloud app versions migrate previous-version-id \
  --service=default

# Delete problematic version
gcloud app versions delete enhanced-v1
```

## Security Considerations

1. **API Key Security**:
   - Store OPENAI_API_KEY in Secret Manager
   - Rotate keys regularly
   
2. **Rate Limiting**:
   ```python
   # Add to main.py
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @limiter.limit("100 per minute")
   @app.route('/api/enhanced-variable-picker/search')
   ```

3. **Input Validation**:
   - Sanitize search queries
   - Limit query length to 500 characters
   - Validate top_k parameter (max 100)

## Cost Optimization

1. **Use Parquet**: 80% storage savings
2. **Enable auto-scaling**: Only pay for what you use
3. **Set appropriate timeouts**: Prevent runaway requests
4. **Use Cloud CDN**: Reduce egress costs

## Health Checks

Add enhanced health check endpoint:

```python
@app.route('/api/health/enhanced')
def enhanced_health():
    checks = {
        'parquet_loaded': variable_loader is not None,
        'variables_count': len(variable_loader.get_all_variables()) if variable_loader else 0,
        'enhanced_search': enhanced_picker is not None,
        'embeddings_available': hasattr(enhanced_picker, 'enhanced_search')
    }
    
    status = 'healthy' if all(checks.values()) else 'degraded'
    return jsonify({
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    })
```

## Post-Deployment Checklist

- [ ] Verify Parquet file loads (check logs)
- [ ] Test enhanced search returns 50 results
- [ ] Confirm semantic search is working (if API key set)
- [ ] Check response times are <200ms
- [ ] Verify all domains return relevant results
- [ ] Test category and ID lookups
- [ ] Monitor error rates for first hour
- [ ] Set up alerts for critical metrics

## Support

For deployment issues:
- Check logs: `gcloud app logs read`
- GitHub Issues: https://github.com/yourusername/activation-manager/issues
- Stack Overflow: Tag with `activation-manager`