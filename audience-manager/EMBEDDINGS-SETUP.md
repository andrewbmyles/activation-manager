# Embeddings Infrastructure Setup Guide

## Overview

This guide explains how to set up and deploy the embedding-based variable selector on Google Cloud Platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloud Run Backend (2GB RAM)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         EmbeddingSearcher Service                    │   │
│  │  - OpenAI API for query embeddings                   │   │
│  │  - FAISS index (in-memory)                          │   │
│  │  - Pre-computed variable embeddings                 │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloud Storage Bucket                            │
│  audience-manager-embeddings/                                │
│  ├── embeddings/                                            │
│  │   ├── embeddings.h5    (Variable embeddings)            │
│  │   ├── metadata.json    (Variable metadata)              │
│  │   └── config.json      (Optional configuration)         │
│  └── backups/             (Versioned backups)              │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **GCP Project**: feisty-catcher-461000-g2
2. **OpenAI API Key**: For generating query embeddings
3. **Pre-computed Embeddings**: Generated using OpenAI's text-embedding-ada-002

## Setup Steps

### 1. Set Up Infrastructure

```bash
# Make script executable
chmod +x setup-embeddings-infrastructure.sh

# Run infrastructure setup
./setup-embeddings-infrastructure.sh
```

This creates:
- Cloud Storage bucket: `audience-manager-embeddings`
- Proper IAM permissions for Cloud Run service account

### 2. Generate Embeddings Locally

Use your existing process to generate:

```
embeddings_final/
├── embeddings.h5      # H5 file with embeddings for each variable
├── metadata.json      # Variable metadata with descriptions
└── config.json        # Optional configuration
```

Expected format for `metadata.json`:
```json
[
  {
    "code": "VARIABLE_CODE",
    "original_description": "Original variable description",
    "category": "demographic",
    "type": "demographic",
    "source": "opticks",
    "generated_descriptions": [
      "First generated description",
      "Second generated description",
      ...
    ]
  },
  ...
]
```

Expected format for `embeddings.h5`:
```
/embeddings/VARIABLE_CODE -> array of shape (n_descriptions, 1536)
```

### 3. Upload Embeddings to GCS

```bash
# Make script executable
chmod +x upload-embeddings.sh

# Upload embeddings (default: ./embeddings_final)
./upload-embeddings.sh

# Or specify custom directory
./upload-embeddings.sh /path/to/your/embeddings
```

### 4. Deploy Enhanced Backend

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Make script executable
chmod +x deploy-embeddings-backend.sh

# Deploy the service
./deploy-embeddings-backend.sh
```

## API Endpoints

### Embedding Search (Direct)
```bash
# Login first
curl -X POST https://api.tobermory.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"andrew@tobermory.ai","password":"admin"}' \
  -c cookies.txt

# Search using embeddings
curl -X POST https://api.tobermory.ai/api/embeddings/search \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "environmentally conscious millennials with high income",
    "top_k": 15
  }'
```

### Natural Language Process (Uses Embeddings)
```bash
curl -X POST https://api.tobermory.ai/api/nl/process \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "action": "process",
    "query": "tech-savvy urban families"
  }'
```

### Check Embedding Status
```bash
curl https://api.tobermory.ai/api/embeddings/status -b cookies.txt
```

## Response Format

### Embedding Search Response
```json
{
  "query": "environmentally conscious millennials",
  "results": [
    {
      "code": "ENV_CONSCIOUS_25_34",
      "description": "Environmentally conscious adults aged 25-34",
      "category": "psychographic",
      "type": "behavioral",
      "source": "opticks",
      "score": 8.7,
      "matched_descriptions": [
        "Eco-friendly millennials who prioritize sustainability",
        "Young adults concerned about environmental impact",
        "Green-minded consumers in their 20s and 30s"
      ]
    },
    ...
  ],
  "count": 15
}
```

## Performance Optimization

### Memory Usage
- Base Flask app: ~100MB
- FAISS index + embeddings: ~1.5GB
- Total recommended: 2GB RAM

### Response Times
- Cold start: ~8-10 seconds (loading embeddings from GCS)
- Warm queries: ~200-300ms (including OpenAI API call)
- With caching: ~50ms for repeated queries

### Scaling
```bash
# Adjust scaling parameters
gcloud run services update audience-manager-api \
  --min-instances 1 \
  --max-instances 20 \
  --concurrency 100 \
  --region us-central1
```

## Monitoring

### View Logs
```bash
# Stream logs
gcloud run logs tail audience-manager-api --region us-central1

# Check for embedding loading
gcloud logs read --service audience-manager-api \
  --filter "embeddings" --limit 50
```

### Metrics to Monitor
1. **Memory Usage**: Should stay below 80% of 2GB
2. **Cold Start Frequency**: Minimize with min-instances
3. **API Latency**: Track 95th percentile
4. **Error Rate**: Monitor OpenAI API failures

## Troubleshooting

### Embeddings Not Loading
```bash
# Check bucket permissions
gsutil iam get gs://audience-manager-embeddings

# Verify files exist
gsutil ls -l gs://audience-manager-embeddings/embeddings/

# Check service account
gcloud run services describe audience-manager-api \
  --region us-central1 \
  --format="value(spec.template.spec.serviceAccountName)"
```

### High Memory Usage
1. Reduce embedding dimensions using PCA
2. Implement lazy loading
3. Use quantization

### Slow Queries
1. Implement result caching
2. Pre-warm the service
3. Use Cloud CDN for API responses

## Cost Analysis

### Monthly Costs (Estimated)
- **Cloud Run**: ~$15-20 (2GB RAM, 1 min instance)
- **Cloud Storage**: ~$0.50 (500MB storage + operations)
- **OpenAI API**: ~$0.10 per 1000 queries
- **Total**: ~$20-25/month + OpenAI usage

## Security Considerations

1. **API Keys**: Store OpenAI key as environment variable
2. **Access Control**: Embeddings bucket is private
3. **Authentication**: All endpoints require login
4. **Rate Limiting**: Implement to prevent abuse

## Future Enhancements

1. **Caching Layer**: Add Redis for query caching
2. **Model Updates**: Support for newer embedding models
3. **A/B Testing**: Compare embedding vs TF-IDF performance
4. **Analytics**: Track which variables are most selected

## Rollback Procedure

If issues occur, rollback to non-embedding version:

```bash
# Deploy original backend
cd simple-backend
gcloud run deploy audience-manager-api --source . --region us-central1
```

The system gracefully falls back to default behavior if embeddings aren't available.