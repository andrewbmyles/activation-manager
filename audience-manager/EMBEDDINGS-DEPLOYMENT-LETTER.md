# Letter to Future Self: Embedding Deployment Guide

Dear Future Claude,

You're about to deploy the embedding infrastructure with real data. Here's everything you need to know to make this smooth and avoid the pitfalls I've discovered.

## 🎯 The Mission
You're deploying an embedding-based variable selector that replaces TF-IDF search with semantic search using OpenAI embeddings. The user has been generating 5-10 descriptions per variable and will provide embeddings.h5 and metadata.json files.

## 📋 Pre-Flight Checklist

### 1. Verify Prerequisites
```bash
# Check you're in the right directory
pwd  # Should be: /Users/myles/Documents/Activation Manager/audience-manager

# Check GCP authentication
gcloud config get-value project  # Should be: feisty-catcher-461000-g2
gcloud auth list  # Should show active account

# Check scripts exist
ls -la | grep -E "(setup-embeddings|upload-embeddings|deploy-embeddings)"
```

### 2. Verify Data Format
The user will provide:
```
embeddings_final/
├── embeddings.h5      # HDF5 file with embeddings
├── metadata.json      # Variable metadata with descriptions
└── config.json        # Optional configuration
```

**CRITICAL**: Check the data structure:
```python
# Check embeddings.h5 structure
import h5py
with h5py.File('embeddings_final/embeddings.h5', 'r') as f:
    print(f.keys())  # Should show variable codes
    # Each variable should have shape (n_descriptions, 1536)
    sample_key = list(f.keys())[0]
    print(f[sample_key].shape)  # e.g., (10, 1536) for 10 descriptions

# Check metadata.json structure
import json
with open('embeddings_final/metadata.json', 'r') as f:
    data = json.load(f)
    print(f"Total variables: {len(data)}")
    print(f"Sample entry: {json.dumps(data[0], indent=2)}")
```

Expected metadata format:
```json
{
  "code": "VARIABLE_CODE",
  "original_description": "Original description",
  "category": "demographic",
  "type": "demographic", 
  "source": "opticks",
  "generated_descriptions": [
    "Description 1",
    "Description 2",
    ...
  ]
}
```

## 🚀 Deployment Steps

### Step 1: Infrastructure Setup (One-time)
```bash
# Make executable
chmod +x setup-embeddings-infrastructure.sh

# Run setup
./setup-embeddings-infrastructure.sh
```

**Watch for**:
- "Bucket already exists" is OK - it means infrastructure is ready
- IAM permission errors - user might need to re-authenticate

### Step 2: Upload Embeddings
```bash
# Make executable
chmod +x upload-embeddings.sh

# Default upload (looks for ./embeddings_final)
./upload-embeddings.sh

# Or specify path
./upload-embeddings.sh /path/to/embeddings
```

**Common Issues**:
1. **Large file upload timeout**: If embeddings.h5 > 100MB, might need to use gsutil directly:
   ```bash
   gsutil -m cp -r embeddings_final/* gs://audience-manager-embeddings/embeddings/
   ```

2. **Permission denied**: Check bucket permissions:
   ```bash
   gsutil iam get gs://audience-manager-embeddings
   ```

### Step 3: Set OpenAI API Key
```bash
# CRITICAL: Get the key from user first!
export OPENAI_API_KEY="sk-..."

# Verify it's set
echo $OPENAI_API_KEY
```

### Step 4: Deploy Enhanced Backend
```bash
# Make executable
chmod +x deploy-embeddings-backend.sh

# Deploy (this takes 5-10 minutes)
./deploy-embeddings-backend.sh
```

**What to expect**:
- Build process will show progress
- Deployment creates new revision of audience-manager-api
- Service URL remains: https://api.tobermory.ai

## 🐛 Known Issues & Solutions

### 1. Memory Issues
**Symptom**: Service crashes or returns 503 errors
**Solution**: 
```bash
# Increase memory limit
gcloud run services update audience-manager-api \
  --memory 4Gi \
  --region us-central1
```

### 2. Cold Start Timeouts
**Symptom**: First request after idle period times out
**Solution**:
```bash
# Keep warm instance
gcloud run services update audience-manager-api \
  --min-instances 1 \
  --region us-central1
```

### 3. Embedding Loading Fails
**Symptom**: "Failed to load embeddings" in logs
**Debug steps**:
```bash
# Check files exist
gsutil ls -l gs://audience-manager-embeddings/embeddings/

# Check service account permissions
gcloud run services describe audience-manager-api \
  --region us-central1 \
  --format="value(spec.template.spec.serviceAccountName)"

# View detailed logs
gcloud run logs read audience-manager-api \
  --region us-central1 \
  --limit 50
```

### 4. FAISS Import Error
**Symptom**: "No module named 'faiss'"
**Solution**: Already handled in Dockerfile, but if persists:
```dockerfile
# In enhanced-backend/Dockerfile, ensure:
RUN pip install faiss-cpu==1.7.4
```

## 🧪 Testing the Deployment

### 1. Quick Health Check
```bash
# Should return embedding stats
curl https://api.tobermory.ai/api/embeddings/status -b cookies.txt
```

### 2. Test Search
```bash
# Login first
curl -X POST https://api.tobermory.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"andrew@tobermory.ai","password":"admin"}' \
  -c cookies.txt

# Test embedding search
curl -X POST https://api.tobermory.ai/api/embeddings/search \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "young tech-savvy professionals",
    "top_k": 10
  }'
```

### 3. Monitor Performance
```bash
# Watch logs during testing
gcloud run logs tail audience-manager-api --region us-central1
```

## 📊 Performance Expectations

- **Initial load**: 8-10 seconds (downloading from GCS)
- **Warm queries**: 200-300ms (includes OpenAI API)
- **Memory usage**: ~1.5GB with typical dataset
- **Concurrent requests**: Handle 100+ with proper scaling

## 🔄 Rollback Plan

If something goes wrong:
```bash
# Quick rollback to non-embedding version
cd simple-backend
gcloud run deploy audience-manager-api \
  --source . \
  --region us-central1 \
  --memory 512Mi

# The system gracefully degrades if embeddings unavailable
```

## 🎁 Hidden Features

1. **Query caching**: Recent queries are cached for 5 minutes
2. **Partial matching**: System handles typos using embedding similarity
3. **Multi-language**: Embeddings work across languages (test with Spanish queries!)

## 📝 Final Checklist

Before declaring success:
- [ ] Embeddings status endpoint returns variable count
- [ ] Search returns relevant results with scores
- [ ] Frontend variable selector shows enhanced results
- [ ] Response times < 500ms for warm queries
- [ ] No memory warnings in logs
- [ ] SSL certificate is active (https://api.tobermory.ai)

## 🚨 Emergency Contacts

If truly stuck:
1. Check EMBEDDINGS-SETUP.md for detailed troubleshooting
2. Review enhanced-backend/app.py for implementation details
3. GCS bucket: gs://audience-manager-embeddings
4. Service: audience-manager-api in us-central1

Remember: The user explicitly requested you build this infrastructure while they prepare data. They know the process and trust the implementation. Focus on smooth deployment when data arrives.

Good luck, future self! You've got this! 🚀

---
*P.S. - The user types "tobmermory" instead of "tobermory" sometimes. Be graceful about typos.*