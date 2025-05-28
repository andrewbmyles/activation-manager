# Vercel Frontend + GCP Backend Deployment Guide

## 🚀 Overview

This guide walks you through deploying the Audience Manager with:
- **Frontend**: Vercel (React app)
- **Backend**: Google Cloud Platform App Engine (Python API)
- **Database**: Redis (Google Memorystore)
- **Storage**: Google Cloud Storage (for large datasets)

## 📋 Prerequisites

1. **Accounts**:
   - Vercel account (https://vercel.com)
   - Google Cloud Platform account with billing enabled
   - GitHub account (for CI/CD)

2. **Tools**:
   - Node.js 20+ and npm
   - Python 3.11+
   - Google Cloud SDK (`gcloud`)
   - Vercel CLI (`npm i -g vercel`)

3. **GCP APIs to Enable**:
   - App Engine API
   - Cloud Build API
   - Secret Manager API
   - Cloud Storage API
   - Redis API (Memorystore)

## 🔧 Step 1: Prepare Your GCP Project

```bash
# Install Google Cloud SDK if needed
# Visit: https://cloud.google.com/sdk/docs/install

# Login to GCP
gcloud auth login

# Create a new project (or use existing)
gcloud projects create audience-manager-prod --name="Audience Manager"

# Set the project
gcloud config set project audience-manager-prod

# Enable billing (required for App Engine)
# Visit: https://console.cloud.google.com/billing
```

## 🚀 Step 2: Deploy Backend to GCP

### Quick Deploy

```bash
# Run the deployment script
cd audience-manager
./gcp/deploy-backend.sh \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --dataset-bucket your-dataset-bucket
```

### Manual Deploy Steps

1. **Enable Required APIs**:
```bash
gcloud services enable \
  appengine.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  storage.googleapis.com
```

2. **Create App Engine App**:
```bash
gcloud app create --region=us-central1
```

3. **Set Up Secrets**:
```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
echo -n "redis://your-redis-host:6379" | gcloud secrets create database-url --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding secret-key \
  --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

4. **Create Redis Instance**:
```bash
gcloud redis instances create audience-manager-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x
```

5. **Deploy Backend**:
```bash
cd gcp
gcloud app deploy app.yaml --quiet
```

## 🌐 Step 3: Deploy Frontend to Vercel

### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
cd audience-manager
vercel

# Follow prompts to:
# - Link to your Vercel account
# - Configure project settings
# - Set environment variables
```

### Option B: Using Vercel Dashboard

1. Visit https://vercel.com/new
2. Import your GitHub repository
3. Configure build settings:
   - Framework: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`
4. Add environment variable:
   - `REACT_APP_API_URL`: `https://YOUR_PROJECT_ID.appspot.com`

### Option C: GitHub Integration

1. Push your code to GitHub
2. Connect GitHub repo to Vercel
3. Vercel will auto-deploy on every push

## 🔐 Step 4: Configure Environment Variables

### Backend (GCP)

Update `gcp/app.yaml`:
```yaml
env_variables:
  FLASK_ENV: "production"
  REDIS_HOST: "YOUR_REDIS_IP"
  PROJECT_ID: "YOUR_PROJECT_ID"
  DATASET_BUCKET: "YOUR_BUCKET_NAME"
```

### Frontend (Vercel)

In Vercel Dashboard → Settings → Environment Variables:
```
REACT_APP_API_URL=https://YOUR_PROJECT_ID.appspot.com
```

## 📊 Step 5: Upload Dataset to GCS

```bash
# Create a bucket
gsutil mb -p YOUR_PROJECT_ID gs://audience-manager-datasets

# Upload your dataset
gsutil cp synthetic_consumer_data_100000.csv gs://audience-manager-datasets/

# Or use the sample data generator
cd src/api
python -c "
from enhanced_nl_audience_builder import DataRetriever
dr = DataRetriever('', '')
df = dr.fetch_data(['AGE_RANGE', 'INCOME_LEVEL', 'LOCATION_TYPE'], 10000)
df.to_csv('sample_data.csv', index=False)
"
gsutil cp sample_data.csv gs://audience-manager-datasets/
```

## 🧪 Step 6: Test Your Deployment

### Test Backend
```bash
# Check health endpoint
curl https://YOUR_PROJECT_ID.appspot.com/health

# Test API endpoint
curl -X POST https://YOUR_PROJECT_ID.appspot.com/api/audience/process \
  -H "Content-Type: application/json" \
  -d '{"action": "search", "payload": {"query": "millennials in urban areas"}}'
```

### Test Frontend
```bash
# Visit your Vercel URL
open https://your-app.vercel.app

# Check browser console for API connections
# Try creating an audience segment
```

## 📈 Step 7: Monitor and Scale

### GCP Monitoring

1. **View Logs**:
```bash
gcloud app logs tail -s default
```

2. **Monitor Dashboard**:
   - Visit: https://console.cloud.google.com/appengine
   - Check: Request latency, error rate, instance count

3. **Scale Settings**:
```yaml
# Update gcp/app.yaml
automatic_scaling:
  min_instances: 2
  max_instances: 20
  target_cpu_utilization: 0.65
```

### Vercel Analytics

1. Enable Analytics in Vercel Dashboard
2. Add Web Vitals tracking
3. Monitor performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure Flask-CORS is configured
   - Check API URL in frontend matches backend

2. **502 Bad Gateway**:
   - Check App Engine logs
   - Increase instance memory/CPU
   - Check Redis connection

3. **Slow API Responses**:
   - Enable caching with Redis
   - Optimize clustering algorithm
   - Use Cloud CDN for static assets

### Debug Commands

```bash
# Check App Engine status
gcloud app describe

# View recent logs
gcloud app logs read --limit=50

# SSH into instance (for debugging)
gcloud app instances ssh INSTANCE_ID --service=default

# Test Redis connection
gcloud redis instances describe audience-manager-redis --region=us-central1
```

## 💰 Cost Optimization

### Estimated Monthly Costs

- **App Engine**: ~$50-200 (depends on traffic)
- **Redis (1GB)**: ~$35
- **Cloud Storage**: ~$0.02/GB
- **Secrets Manager**: ~$0.06/secret
- **Total**: ~$100-300/month

### Cost Saving Tips

1. Use App Engine automatic scaling
2. Set appropriate min/max instances
3. Enable Cloud CDN for static assets
4. Use lifecycle rules for Cloud Storage
5. Monitor and optimize Redis usage

## 🔒 Security Best Practices

1. **Enable IAM**:
```bash
# Limit service account permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/appengine.appAdmin"
```

2. **Use Secret Manager** for all sensitive data
3. **Enable Cloud Armor** for DDoS protection
4. **Set up Cloud IAP** for admin access
5. **Regular security scans** with Cloud Security Scanner

## 📚 Next Steps

1. **Set up CI/CD**:
   - Use Cloud Build for automated deployments
   - Configure GitHub Actions workflow

2. **Add Monitoring**:
   - Set up Cloud Monitoring alerts
   - Integrate with PagerDuty/Slack

3. **Optimize Performance**:
   - Enable Cloud CDN
   - Implement caching strategies
   - Use Cloud Tasks for async processing

4. **Backup Strategy**:
   - Regular Cloud Storage backups
   - Redis persistence configuration

---

## 🆘 Quick Reference

**Backend URL**: `https://YOUR_PROJECT_ID.appspot.com`  
**Frontend URL**: `https://your-app.vercel.app`  
**GCP Console**: `https://console.cloud.google.com/appengine?project=YOUR_PROJECT_ID`  
**Vercel Dashboard**: `https://vercel.com/dashboard`

**Support Commands**:
```bash
# View backend logs
gcloud app logs tail -s default

# Redeploy backend
cd gcp && gcloud app deploy

# Redeploy frontend
vercel --prod

# Check service status
gcloud app services list
```