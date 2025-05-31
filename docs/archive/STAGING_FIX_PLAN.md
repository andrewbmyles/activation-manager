# Staging Environment Fix Plan

## Problem Summary

The staging deployment has multiple issues preventing proper search functionality:

1. **Enhanced search not initializing** - Returns "Search not initialized" error
2. **Embeddings not loading** - GCS download fails with "No files downloaded from GCS"
3. **Inconsistent behavior** - Sometimes works, sometimes doesn't (race condition)
4. **Poor search results** - When it does work, returns irrelevant results (automotive instead of income)

## Root Causes

### 1. Lazy Initialization Race Condition
- The enhanced picker uses lazy initialization (`_ensure_initialized`)
- Multiple workers in App Engine may initialize simultaneously
- Cache might not be shared properly between instances

### 2. Missing GCS Embeddings
- The app expects embeddings in GCS bucket but they're not there
- Falls back to keyword-only search with poor results
- No proper error handling for missing embeddings

### 3. Data Format Mismatch
- Parquet loader loads 49,323 variables successfully
- But enhanced search isn't properly converting them to the expected format
- Variable structure mismatch between loaders

## Detailed Fix Plan

### Phase 1: Immediate Fixes (Quick Wins)

#### 1.1 Fix Enhanced Search Initialization
```python
# In enhanced_variable_picker_api.py
def _ensure_initialized(self):
    """Fix initialization to be more robust"""
    if self._initialized:
        return True
    
    try:
        # Add retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Initialize components
                ...
                self._initialized = True
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Brief delay before retry
                    continue
                raise
    except Exception as e:
        logger.error(f"Failed to initialize after {max_retries} attempts: {e}")
        self._initialized = False
        return False
```

#### 1.2 Add Fallback Search
```python
# Always provide basic search even if enhanced fails
if not self._ensure_initialized():
    # Use basic parquet search directly
    if hasattr(self, 'parquet_loader') and self.parquet_loader:
        return self._basic_parquet_search(query, top_k)
```

#### 1.3 Skip Embeddings for Now
```python
# In app_production.yaml
env_variables:
  USE_EMBEDDINGS: "false"  # Disable until GCS is fixed
  EMBEDDING_LOAD_STRATEGY: "skip"
```

### Phase 2: Proper Embedding Setup

#### 2.1 Upload Embeddings to GCS
```bash
# Create embeddings bucket if not exists
gsutil mb gs://activation-manager-embeddings

# Upload embeddings
gsutil cp activation_manager/data/embeddings/*.npy \
  gs://activation-manager-embeddings/

# Set permissions
gsutil iam ch allUsers:objectViewer \
  gs://activation-manager-embeddings
```

#### 2.2 Fix GCS Loading Code
```python
# In variable_selector.py
def _load_from_gcs(self):
    """Improved GCS loading with better error handling"""
    try:
        bucket_name = os.environ.get('GCS_BUCKET', 'activation-manager-embeddings')
        
        # List available files first
        blobs = list(bucket.list_blobs())
        if not blobs:
            logger.warning(f"No files found in bucket {bucket_name}")
            return False
            
        # Download embeddings
        for blob in blobs:
            if blob.name.endswith('.npy'):
                local_path = f"/tmp/{blob.name}"
                blob.download_to_filename(local_path)
                logger.info(f"Downloaded {blob.name}")
                
        return True
    except Exception as e:
        logger.error(f"GCS download failed: {e}")
        return False
```

### Phase 3: Improve Search Quality

#### 3.1 Fix Variable Conversion
```python
# In enhanced_semantic_search_v2.py
def __init__(self, variables: List[Dict[str, Any]], ...):
    """Ensure variables are properly formatted"""
    
    # Convert variables to EnhancedVariable objects
    self.variables = []
    for var in variables:
        if isinstance(var, dict):
            # Map fields correctly
            enhanced_var = EnhancedVariable(
                code=var.get('name', var.get('code', '')),
                description=var.get('description', ''),
                category=var.get('category', ''),
                theme=var.get('theme', ''),
                product=var.get('product_name', ''),
                domain=var.get('domain', 'general')
            )
            self.variables.append(enhanced_var)
```

#### 3.2 Add Search Debugging
```python
# Add debug logging to understand search behavior
logger.info(f"Search query: '{query}'")
logger.info(f"Found {len(keyword_results)} keyword results")
logger.info(f"Sample results: {[r['description'][:50] for r in results[:3]]}")
```

### Phase 4: Deployment Strategy

#### 4.1 Test Locally First
```bash
# Test with production config locally
export USE_EMBEDDINGS=false
export GAE_ENV=standard
python main.py
```

#### 4.2 Deploy Incremental Fix
```bash
# Deploy phase 1 fixes first
gcloud app deploy app_production.yaml \
  --version=fix-$(date +%Y%m%d-%H%M%S) \
  --no-promote
```

#### 4.3 Monitor and Verify
```bash
# Check logs
gcloud app logs tail --version=fix-VERSION

# Test search
curl -X POST https://fix-VERSION-dot-PROJECT.appspot.com/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{"query": "income", "top_k": 10}'
```

## Implementation Priority

1. **Immediate (Today)**
   - Fix initialization race condition
   - Add fallback to basic search
   - Disable embeddings temporarily

2. **Short Term (This Week)**
   - Upload embeddings to GCS
   - Fix GCS loading code
   - Improve error handling

3. **Medium Term (Next Week)**
   - Fix variable conversion
   - Add comprehensive logging
   - Optimize search quality

## Success Criteria

- [ ] Search returns results for basic queries (age, income, etc.)
- [ ] No "Search not initialized" errors
- [ ] Similarity filtering reduces results by 30-50%
- [ ] Response time under 2 seconds
- [ ] Works consistently across multiple requests

## Monitoring Plan

1. Set up alerts for:
   - "Search not initialized" errors
   - Response time > 3 seconds
   - Error rate > 5%

2. Track metrics:
   - Search success rate
   - Average response time
   - Filtering effectiveness
   - Result relevance

## Rollback Plan

If issues persist:
1. Revert to previous working version
2. Disable enhanced search, use basic search only
3. Route traffic to stable version

## Next Steps

1. Review and approve this plan
2. Create feature branch for fixes
3. Implement Phase 1 fixes
4. Test locally
5. Deploy to new staging version
6. Verify fixes work
7. Promote to production