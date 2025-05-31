# Activation Manager - Deployment Options Guide

## Overview
This guide covers various deployment options for the Activation Manager, from simple static hosting to enterprise-grade solutions. The application consists of:
- **Frontend**: React SPA (Static files)
- **Backend**: Python Flask API
- **Data**: 100k+ records (1.7GB CSV file)

## Quick Comparison

| Platform | Frontend | Backend | Cost | Scalability | Complexity | Best For |
|----------|----------|---------|------|-------------|------------|----------|
| Vercel | ✅ Excellent | ✅ Serverless | Free-$20/mo | High | Low | Rapid deployment |
| Netlify | ✅ Excellent | ⚠️ Functions | Free-$19/mo | Medium | Low | Static sites |
| AWS | ✅ Full control | ✅ Full control | Pay-per-use | Unlimited | High | Enterprise |
| Heroku | ✅ Good | ✅ Excellent | $7-500/mo | High | Low | Full-stack apps |
| Railway | ✅ Good | ✅ Excellent | $5-20/mo | High | Low | Modern deployment |
| Render | ✅ Good | ✅ Excellent | Free-$25/mo | High | Low | Full-stack apps |
| Google Cloud | ✅ Full control | ✅ Full control | Pay-per-use | Unlimited | High | Enterprise |
| Azure | ✅ Full control | ✅ Full control | Pay-per-use | Unlimited | High | Enterprise |

## 1. Vercel (Recommended for Quick Start)

### Pros
- Excellent React/Next.js support
- Automatic HTTPS and CDN
- Serverless Python support
- GitHub integration
- Great developer experience

### Cons
- 10MB function size limit
- 10s function timeout on free tier
- Large dataset handling requires external storage

### Deployment Steps
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
cd audience-manager
vercel

# Set environment variables in Vercel dashboard
# REACT_APP_API_URL=/api
```

### Data Solution for Vercel
```python
# Option 1: Use external database (Supabase, PostgreSQL)
# Option 2: Sample dataset for demo
# Option 3: S3/CloudStorage for full dataset
```

### Configuration
Already configured in your project:
- `vercel.json` - Routes and serverless config
- `api/index.py` - Serverless function entry

## 2. AWS (Best for Enterprise)

### Architecture Options

#### Option A: Traditional (EC2 + S3 + CloudFront)
```
CloudFront (CDN)
    ├── S3 (React Static Files)
    └── ALB → EC2 (Flask API)
         └── RDS/DynamoDB (Data)
```

#### Option B: Serverless (S3 + Lambda + API Gateway)
```
CloudFront (CDN)
    ├── S3 (React Static Files)
    └── API Gateway → Lambda (Flask)
         └── DynamoDB/S3 (Data)
```

### Deployment with AWS CDK
```python
# cdk_stack.py
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
)

class ActivationManagerStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 bucket for React app
        bucket = s3.Bucket(self, "FrontendBucket",
            website_index_document="index.html",
            public_read_access=True
        )
        
        # CloudFront distribution
        distribution = cloudfront.Distribution(self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket)
            )
        )
        
        # Lambda for API
        api_lambda = lambda_.Function(self, "APIFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("activation_manager"),
            handler="api.enhanced_audience_api.handler",
            memory_size=3008,
            timeout=Duration.seconds(30)
        )
```

### Cost Estimate
- **Small (1k users/day)**: ~$50-100/month
- **Medium (10k users/day)**: ~$200-500/month
- **Large (100k+ users/day)**: ~$1000+/month

## 3. Heroku (Simple Full-Stack)

### Deployment Steps
```bash
# Create Heroku app
heroku create activation-manager

# Add Python buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Add PostgreSQL for data
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_APP=activation_manager/api/enhanced_audience_api.py
```

### Procfile
```
web: cd activation_manager && gunicorn api.enhanced_audience_api:app
release: python scripts/migrate_data.py
```

### Cost
- **Hobby**: $7/month per dyno
- **Standard**: $25-50/month
- **Performance**: $250-500/month

## 4. Railway (Modern Alternative)

### Why Railway?
- Simple deployment from GitHub
- Built-in PostgreSQL
- Automatic HTTPS
- Great pricing model

### Deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up

# Add database
railway add postgresql
```

## 5. Docker Deployment (Any Platform)

### Multi-Stage Dockerfile
```dockerfile
# Frontend build stage
FROM node:18-alpine as frontend-build
WORKDIR /app
COPY audience-manager/package*.json ./
RUN npm ci
COPY audience-manager/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY activation_manager/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY activation_manager/ ./activation_manager/

# Copy frontend build
COPY --from=frontend-build /app/build ./static

# Data handling
ENV DATA_PATH=/data/synthetic_data.csv
VOLUME ["/data"]

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "activation_manager.api.enhanced_audience_api:app"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/activation
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/data
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=activation
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

## 6. Kubernetes Deployment

### Helm Chart Structure
```yaml
# values.yaml
replicaCount: 3

image:
  repository: activation-manager
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  hosts:
    - host: activation-manager.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

postgresql:
  enabled: true
  auth:
    database: activation

redis:
  enabled: true
```

## 7. Static Hosting + Serverless Backend

### Frontend (GitHub Pages, Netlify, Surge)
```bash
# Build frontend
cd audience-manager
npm run build

# Deploy to GitHub Pages
npm install -g gh-pages
gh-pages -d build

# Or Netlify
npm install -g netlify-cli
netlify deploy --prod --dir=build

# Or Surge
npm install -g surge
surge build/ activation-manager.surge.sh
```

### Backend Options
1. **AWS Lambda**
2. **Google Cloud Functions**
3. **Azure Functions**
4. **Cloudflare Workers**

## Data Handling Strategies

### 1. Database Migration
```python
# scripts/migrate_to_postgres.py
import pandas as pd
from sqlalchemy import create_engine

# Load CSV
df = pd.read_csv('synthetic_data.csv')

# Connect to database
engine = create_engine('postgresql://user:pass@host/db')

# Upload in chunks
chunk_size = 10000
for i in range(0, len(df), chunk_size):
    chunk = df[i:i+chunk_size]
    chunk.to_sql('consumer_data', engine, if_exists='append')
```

### 2. Cloud Storage
```python
# Upload to S3
import boto3

s3 = boto3.client('s3')
s3.upload_file('synthetic_data.csv', 'my-bucket', 'data/synthetic_data.csv')

# In your API
def load_data_from_s3():
    df = pd.read_csv('s3://my-bucket/data/synthetic_data.csv')
    return df
```

### 3. Data Sampling for Demos
```python
# Create smaller dataset for demos
df_full = pd.read_csv('synthetic_data_100k.csv')
df_sample = df_full.sample(n=10000, random_state=42)
df_sample.to_csv('synthetic_data_10k_demo.csv', index=False)
```

## Security Considerations

### 1. Environment Variables
```bash
# .env.production
REACT_APP_API_URL=https://api.activation-manager.com
API_KEY=your-secret-key
DATABASE_URL=postgres://...
JWT_SECRET=your-jwt-secret
```

### 2. HTTPS Setup
- Use platform's automatic HTTPS (Vercel, Netlify)
- Or set up Let's Encrypt for custom domains

### 3. Authentication
```python
# Add to your API
from flask_jwt_extended import JWTManager, create_access_token

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET')
jwt = JWTManager(app)
```

## Monitoring & Analytics

### 1. Application Monitoring
- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **DataDog**: Full observability

### 2. Analytics
- **Google Analytics**: User behavior
- **Mixpanel**: Event tracking
- **Plausible**: Privacy-focused analytics

## Recommended Deployment Path

### For Demo/POC
1. **Frontend**: Vercel (free tier)
2. **Backend**: Vercel Serverless Functions
3. **Data**: 10k sample dataset

### For Production
1. **Frontend**: CloudFront + S3
2. **Backend**: ECS or Lambda
3. **Data**: RDS PostgreSQL or DynamoDB
4. **Cache**: ElastiCache Redis

### For Enterprise
1. **Frontend**: CloudFront + S3
2. **Backend**: EKS (Kubernetes)
3. **Data**: Aurora PostgreSQL
4. **Cache**: ElastiCache
5. **Queue**: SQS/EventBridge
6. **Monitoring**: CloudWatch + X-Ray

## Deployment Checklist

- [ ] Choose deployment platform
- [ ] Set up environment variables
- [ ] Configure data storage solution
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS settings
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Test deployment
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process

## Cost Optimization Tips

1. **Use CDN** for static assets
2. **Implement caching** at multiple levels
3. **Use serverless** for variable load
4. **Compress data** before storage
5. **Use spot instances** for batch processing
6. **Set up auto-scaling** rules
7. **Monitor and optimize** regularly

---
*Last Updated: May 25, 2025*