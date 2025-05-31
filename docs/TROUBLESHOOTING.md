# Troubleshooting Guide

Last Updated: May 30, 2025

## Common Issues and Solutions

### 1. Flask Server Hanging on Startup (FIXED in v1.8.0)

**Problem**: Server hangs indefinitely when starting  
**Root Cause**: spaCy attempting to download language models during startup  
**Solution**: 
- Fixed in v1.8.0 by setting `DISABLE_SPACY=true` by default
- If you need spaCy, install models first: `python -m spacy download en_core_web_sm`
- Then set `DISABLE_SPACY=false` in environment

**Environment Variables**:
```bash
# Disable spaCy (default)
export DISABLE_SPACY=true

# Disable embeddings for faster startup
export USE_EMBEDDINGS=false

# Start server
python main.py
```

### 2. Login Issues

**Problem**: Can't log in to the application  
**Solution**: 
- Ensure you're using the correct password
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Check if caps lock is on

### 3. Search Not Working

**Problem**: Variable Picker search returns no results or errors  
**Solutions**:

**Local Development**:
```bash
# Check if backend is running
curl http://localhost:8080/api/health

# If not, start backend with fixes
DISABLE_SPACY=true python main.py

# Test enhanced search
curl -X POST http://localhost:8080/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{"query": "income", "top_k": 5}'

# Check for import errors
python -c "from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI"
```

**Production**:
- Check application logs: `gcloud app logs read --limit=50`
- Verify data files are deployed
- Check embeddings status: https://tobermory.ai/api/embeddings-status
- Look for "fallback mode" in responses (normal during initialization)

### 4. Refine Function Not Working

**Problem**: Clicking "Refine" does nothing or shows error  
**Solution**: 
- This has been fixed in the latest deployment
- Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
- The refine function now works in stateless mode

### 5. Export Not Working

**Problem**: Can't export variables to JSON/CSV  
**Solutions**:
- Ensure you have variables selected and confirmed
- Check browser console for errors (F12)
- Try different browser
- Disable ad blockers

### 6. Similarity Filtering Not Working

**Problem**: Still seeing duplicate/similar variables in results  
**Solutions**:
- Ensure `filter_similar=true` is passed in the request
- Check that similarity threshold is appropriate (default: 0.85)
- Verify the response includes `filter_similar: true`
- For debugging, check logs for "Similarity filtering: X -> Y results"

**Test Command**:
```bash
curl -X POST http://localhost:8080/api/enhanced-variable-picker/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "income",
    "top_k": 50,
    "filter_similar": true,
    "similarity_threshold": 0.85,
    "max_similar_per_group": 2
  }'
```

### 7. Performance Issues

**Problem**: Application is slow or unresponsive  
**Solutions**:

**Check Instance Status**:
```bash
gcloud app instances list
gcloud app services describe default
```

**Optimize Performance**:
- Upgrade instance class in app.yaml
- Check for memory issues
- Review logs for errors

### 6. Build Failures

**Problem**: Frontend build fails  
**Solutions**:

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm run build

# Check Node version
node --version  # Should be 16+

# Clear npm cache
npm cache clean --force
```

### 7. Deployment Failures

**Problem**: Deployment to Google App Engine fails  
**Solutions**:

**Authentication Issues**:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**File Size Issues**:
- Check .gcloudignore file
- Ensure large files are excluded
- Verify data files are included

**Configuration Issues**:
- Verify app.yaml syntax
- Check environment variables
- Ensure all handlers are correct

### 8. Module Import Errors

**Problem**: "No module named 'activation_manager'"  
**Solutions**:

```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/activation-manager"

# Or in code
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### 9. CORS Errors

**Problem**: "CORS policy" errors in browser  
**Solutions**:
- CORS is enabled in production
- For local dev, ensure proxy is configured in package.json
- Check backend is running on correct port (8080)

### 10. Data Loading Issues

**Problem**: "CSV file not found" or similar  
**Solutions**:

```bash
# Check data files exist
ls -la data/

# Required files:
# - data/Full_Variable_List_2022_CAN.csv
# - data/variables_2022_can.parquet (optional)

# Download if missing
gsutil cp gs://your-bucket/data/* ./data/
```

## Debugging Commands

### Local Development

```bash
# Check Python environment
python --version
pip list | grep -E "(flask|pandas|numpy)"

# Test backend
curl http://localhost:8080/api/health

# Check frontend
cd audience-manager
npm list react
```

### Production

```bash
# View logs
gcloud app logs tail -s default

# Check service status
gcloud app services describe default

# View versions
gcloud app versions list

# SSH into instance (if enabled)
gcloud app instances ssh INSTANCE_ID
```

## Log Analysis

### Finding Errors

```bash
# Recent errors
gcloud app logs read --level=error --limit=20

# Search for specific errors
gcloud app logs read --limit=100 | grep -i "error"

# Filter by time
gcloud app logs read --since="2 hours ago"
```

### Common Log Patterns

**Successful Request**:
```
"POST /api/variable-picker/start HTTP/1.1" 200
```

**Failed Request**:
```
"POST /api/variable-picker/refine/session-id HTTP/1.1" 404
```

**Import Error**:
```
ModuleNotFoundError: No module named 'faiss'
```

## Performance Monitoring

### Check Response Times

```bash
# Simple benchmark
time curl https://tobermory.ai/api/health

# Load test (use with caution)
for i in {1..10}; do
  time curl https://tobermory.ai/api/health &
done
wait
```

### Monitor Resources

```bash
# View instance metrics
gcloud app instances describe INSTANCE_ID

# Check billing/usage
gcloud app services list
```

## Emergency Procedures

### Rollback Deployment

```bash
# List versions
gcloud app versions list

# Rollback to previous
gcloud app services set-traffic default --splits=OLD_VERSION=1
```

### Stop All Traffic

```bash
# Stop serving
gcloud app services stop default

# Resume serving
gcloud app services start default
```

### Scale Down

```bash
# Temporary scale down
gcloud app services update default --max-instances=1
```

## Getting Help

1. **Check Logs First**: Most issues are visible in logs
2. **Review Documentation**: Check API docs and deployment guide
3. **Test Locally**: Reproduce issue in local environment
4. **Minimal Example**: Create minimal test case
5. **Contact Support**: Include logs and steps to reproduce

## Preventive Measures

1. **Regular Updates**
   ```bash
   npm update
   pip install -r requirements.txt --upgrade
   ```

2. **Monitor Logs**
   - Set up log alerts
   - Review weekly

3. **Test Before Deploy**
   - Run local tests
   - Deploy to staging first

4. **Backup Data**
   - Keep data file backups
   - Version control configs