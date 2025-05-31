# Parquet Loader Crash Analysis

## Problem Summary
App Engine workers crash ~5 seconds after attempting to import the Parquet loader, causing 500 errors on all endpoints.

## Root Cause Analysis

### 1. **Import Chain Issues**
The crash occurs during import, not execution:
```
✅ Pandas imported successfully
Attempting Parquet loader import...
[CRASH - worker receives SIGTERM after ~5 seconds]
```

### 2. **Possible Causes**

#### A. Memory Constraints (Most Likely)
- **F2 instance** has only **512MB memory**
- Import chain loads:
  - pandas (large library)
  - pyarrow (for parquet support)
  - ParquetVariableLoader class which:
    - Immediately calls `load_variables()` in `__init__`
    - Loads 49,323 variables into memory
    - Creates both DataFrame and dict representations
    - Uses pickle for caching

#### B. Module Import Dependencies
- The import might be triggering additional heavy imports:
  - NumPy (via pandas)
  - PyArrow (for parquet support)
  - Other scientific computing libraries

#### C. File System Access
- SharedCache creates directories in `/tmp`
- Parquet file access might be slow or failing

### 3. **Evidence**
- Works perfectly locally (more memory available)
- Consistent crash timing (~5 seconds = likely OOM killer)
- No error messages (typical of memory exhaustion)
- Multiple workers crash simultaneously

## Proposed Solutions

### Option 1: Increase Resources (Recommended)
**Change instance class from F2 to F4**
- F2: 512MB memory, 0.2 vCPU
- F4: 1GB memory, 0.4 vCPU
- F4_1G: 2GB memory, 0.4 vCPU (if F4 isn't enough)

**Benefits:**
- Simple change (just update app.yaml)
- Keeps all functionality
- Better performance overall

**Cost Impact:**
- F2: $0.05/hour
- F4: $0.10/hour (2x cost)
- F4_1G: $0.12/hour

### Option 2: Lazy Loading
**Modify ParquetVariableLoader to load data on first use, not import**

```python
class ParquetVariableLoader:
    def __init__(self):
        self.variables_df = None
        self.variables_dict = None
        self._loaded = False
    
    def _ensure_loaded(self):
        if not self._loaded:
            self.load_variables()
            self._loaded = True
    
    def get_all_variables(self):
        self._ensure_loaded()
        return self.variables_dict
```

**Benefits:**
- Reduces startup memory spike
- Workers can start without loading data
- Data loads only when needed

### Option 3: Pre-process and Optimize
**Convert data to more efficient format**
- Use compressed pickle instead of parquet
- Load only essential columns
- Use memory-mapped files

### Option 4: External Storage
**Move variable data to Cloud Storage or Memorystore**
- Load data once into shared cache
- Workers retrieve from cache
- Reduces per-worker memory

## Recommended Approach

### Phase 1: Quick Fix (5 minutes)
1. Update `app_cost_optimized.yaml` to use F4 instance
2. Deploy and test
3. If still failing, try F4_1G

### Phase 2: Optimize (if needed)
1. Implement lazy loading
2. Add memory usage logging
3. Optimize data structures

### Phase 3: Long-term (optional)
1. Move to external caching service
2. Implement proper data pipeline
3. Use Cloud SQL or Firestore for variable data

## Implementation Plan

### Step 1: Update Resources
```yaml
# app_cost_optimized.yaml
instance_class: F4  # Increased from F2 for Parquet loader
```

### Step 2: Add Memory Monitoring
```python
import psutil
logger.info(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB")
```

### Step 3: Deploy and Monitor
- Check if workers stay alive
- Monitor memory usage in logs
- Verify variable picker works

## Decision Points

1. **Cost vs Functionality**: Is 2x instance cost acceptable for full functionality?
2. **Performance**: Do we need all 49K variables in memory?
3. **Architecture**: Should we move to external data storage?

## Next Steps

Would you like to:
1. **Try F4 instances** - Simple, likely to work
2. **Implement lazy loading** - More complex, better long-term
3. **Both** - F4 for immediate fix, then optimize