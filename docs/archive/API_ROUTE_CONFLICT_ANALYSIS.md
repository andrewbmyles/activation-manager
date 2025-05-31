# API Route Conflict Analysis

## Problem Summary
The staging deployment (stg-20250530-102625) is returning 500 errors for all API endpoints after adding new route handlers.

## Root Cause Analysis

### 1. Route Conflicts Identified

#### Variable Picker Search Routes:
- Line 401: `@app.route('/api/variable-picker/search', methods=['POST'])` → `variable_picker_search()`
- Line 1073: `@app.route('/api/variable-picker/search', methods=['GET'])` → `variable_picker_search_get()`
- Line 999: `@app.route('/api/enhanced-variable-picker/search', methods=['POST'])` → `enhanced_variable_search()`

**Issue**: Flask allows multiple methods on same route, but the implementation might be causing conflicts.

#### Health Check Routes:
- Line 344: `@app.route('/health', methods=['GET'])` → `health_check()`
- Line 1280: `@app.route('/api/health')` → `api_health_check()`

**Issue**: Two different health check endpoints, but this shouldn't cause 500 errors.

### 2. Potential Issues

1. **Import Dependencies**: The new routes use `variable_loader` which might not be initialized properly in App Engine
2. **DataFrame Access**: The code accesses pandas DataFrame attributes that might fail if data isn't loaded
3. **Global Variables**: Routes depend on globals like `VARIABLE_DATABASE` that might not be populated

### 3. Key Code Issues

In `get_variables_by_category()` (line 1120-1151):
```python
df = variable_loader.variables_df
category_vars = df[df['category'] == category].head(limit)
```
This assumes:
- `variable_loader` exists
- `variable_loader.variables_df` is a valid DataFrame
- The DataFrame has a 'category' column

## Recommended Fix Approach

### Phase 1: Add Defensive Checks
1. Check if `variable_loader` is None before accessing
2. Verify DataFrame exists and has expected columns
3. Add try-catch blocks with specific error messages

### Phase 2: Consolidate Routes
1. Merge GET and POST handlers for same endpoints
2. Use single handler with method checking
3. Remove duplicate functionality

### Phase 3: Improve Error Handling
1. Add detailed logging for each failure point
2. Return specific error messages instead of generic 500s
3. Add fallback behavior when enhanced features aren't available

### Phase 4: Test Locally First
1. Run Flask app locally with same environment
2. Test each endpoint individually
3. Verify error handling works correctly

## Implementation Plan

1. **Immediate Fix**: Add null checks and error handling to new routes
2. **Test Locally**: Verify fixes work before deployment
3. **Deploy Incrementally**: Deploy with verbose logging first
4. **Monitor**: Check logs for specific errors
5. **Iterate**: Fix remaining issues based on actual errors

## Next Steps

1. Fix the route handlers with proper error handling
2. Test locally with `python main.py`
3. Deploy to staging with enhanced logging
4. Run comprehensive tests
5. Promote to production once stable