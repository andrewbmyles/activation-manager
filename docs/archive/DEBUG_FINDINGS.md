# Debug Findings - Enhanced Picker Crash

## Issue Summary
The enhanced variable picker endpoint (`/api/enhanced-variable-picker/search`) causes the Flask server to crash when called. This prevents deployment.

## Root Cause
The issue appears to be with the `get_enhanced_picker()` function in main.py that lazily initializes the Enhanced Variable Picker. When the endpoint is called, it tries to initialize the picker which causes the server process to terminate.

## Evidence
1. Server starts successfully without calling enhanced picker
2. Basic endpoints work fine (`/health`, `/api/variable-picker/search`)
3. Server crashes immediately when enhanced picker endpoint is called
4. Crash happens even with migration disabled
5. Simplified version without enhanced picker works perfectly

## Technical Details
- The crash occurs in Flask's debug mode with multiprocessing warnings
- Likely related to threading/multiprocessing issues with FAISS or the enhanced picker initialization
- The enhanced picker tries to load multiple large resources (embeddings, FAISS index, TF-IDF)

## Temporary Solution
Created `main_simplified_test.py` that:
- Removes enhanced picker initialization
- Uses basic parquet search for all queries
- Maintains similarity filtering functionality
- All migration endpoints work correctly

## Permanent Fix Options

### Option 1: Fix Threading Issue
- Move enhanced picker initialization out of lazy loading
- Initialize at startup instead of on first request
- Use proper thread locks for FAISS

### Option 2: Simplify Enhanced Picker
- Remove the complex initialization
- Use only parquet search with similarity filtering
- Add semantic search later when stable

### Option 3: Separate Service
- Deploy enhanced picker as separate service
- Main app proxies requests to it
- Isolates the problematic code

## Recommendation
For immediate deployment, use Option 2:
1. Simplify the enhanced picker to use parquet search + similarity filtering
2. This maintains the key functionality (98% Contact pattern reduction)
3. Deploy and test the unified search migration framework
4. Add semantic search capabilities later

## Next Steps
1. Update main.py to use simplified enhanced search
2. Test thoroughly
3. Deploy to staging
4. Continue with A/B testing of unified search