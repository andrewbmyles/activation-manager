# Production Deployment Guide

## Overview
This guide covers deploying Activation Manager to production with proper data handling, security, and scalability.

## Recommended Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CloudFlare    │────▶│   React App      │────▶│   API Gateway   │
│      CDN        │     │   (S3 Bucket)    │     │   (HTTPS/Auth)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                        ┌──────────────────────────────────┴────────┐
                        │                                           │
                  ┌─────▼──────┐                          ┌────────▼────────┐
                  │   Lambda    │                          │   ECS Fargate   │
                  │  Functions  │      OR                  │   (Flask API)   │
                  │  (Queries)  │                          │   Auto-scaling  │
                  └─────┬──────┘                          └────────┬────────┘
                        │                                           │
                  ┌─────▼──────────────────────────────────────────▼────────┐
                  │                    PostgreSQL RDS                        │
                  │              (Multi-AZ for High Availability)           │
                  └─────────────────────────────────────────────────────────┘
                                              │
                                        ┌─────▼─────┐
                                        │   Redis   │
                                        │  (Cache)  │
                                        └───────────┘
```

## Step 1: Database Setup

### PostgreSQL Schema
```sql
-- Create database
CREATE DATABASE activation_manager;

-- Variable metadata table
CREATE TABLE variable_metadata (
    variable_code VARCHAR(50) PRIMARY KEY,
    variable_name VARCHAR(255) NOT NULL,
    variable_type VARCHAR(50),
    description TEXT,
    category VARCHAR(100),
    data_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    FULLTEXT idx_description (description)
);

-- Consumer data table (partitioned by postal code for performance)
CREATE TABLE consumer_data (
    id SERIAL,
    postal_code VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    prizm_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, postal_code)
) PARTITION BY HASH (postal_code);

-- Create partitions
CREATE TABLE consumer_data_p0 PARTITION OF consumer_data FOR VALUES WITH (modulus 4, remainder 0);
CREATE TABLE consumer_data_p1 PARTITION OF consumer_data FOR VALUES WITH (modulus 4, remainder 1);
CREATE TABLE consumer_data_p2 PARTITION OF consumer_data FOR VALUES WITH (modulus 4, remainder 2);
CREATE TABLE consumer_data_p3 PARTITION OF consumer_data FOR VALUES WITH (modulus 4, remainder 3);

-- Add dynamic columns for variables
-- This would be done programmatically based on your variable metadata
```

### Data Migration Script
```python
# scripts/migrate_to_production.py
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from tqdm import tqdm

def migrate_data():
    # Database connection
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    cur = conn.cursor()
    
    # Load data
    print("Loading CSV data...")
    df = pd.read_csv('synthetic_consumer_data_100000.csv')
    
    # Migrate in batches
    batch_size = 5000
    total_batches = len(df) // batch_size + 1
    
    print(f"Migrating {len(df)} records in {total_batches} batches...")
    
    for i in tqdm(range(0, len(df), batch_size)):
        batch = df.iloc[i:i+batch_size]
        
        # Prepare data for insertion
        records = batch.to_dict('records')
        
        # Insert batch
        execute_batch(
            cur,
            """
            INSERT INTO consumer_data (postal_code, latitude, longitude, prizm_segment, ...)
            VALUES (%(postal_code)s, %(latitude)s, %(longitude)s, %(prizm_segment)s, ...)
            """,
            records,
            page_size=100
        )
        
        conn.commit()
    
    print("✅ Migration complete!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_data()
```

## Step 2: Backend Deployment (AWS ECS)

### Dockerfile for Production
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn psycopg2-binary redis

# Copy application code
COPY activation_manager/ ./activation_manager/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "activation_manager.api.enhanced_audience_api:app"]
```

### ECS Task Definition
```json
{
  "family": "activation-manager-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-ecr-repo/activation-manager:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        },
        {
          "name": "REDIS_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:redis-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/activation-manager",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Step 3: Frontend Deployment (S3 + CloudFront)

### Build and Deploy Script
```bash
#!/bin/bash
# deploy-frontend.sh

# Build the React app
cd audience-manager
npm run build

# Upload to S3
aws s3 sync build/ s3://activation-manager-frontend/ \
  --delete \
  --cache-control "public, max-age=31536000" \
  --exclude "index.html" \
  --exclude "service-worker.js"

# Upload HTML files with no cache
aws s3 cp build/index.html s3://activation-manager-frontend/ \
  --cache-control "no-cache, no-store, must-revalidate"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --paths "/*"
```

### CloudFront Configuration
```json
{
  "Origins": [{
    "DomainName": "activation-manager-frontend.s3.amazonaws.com",
    "S3OriginConfig": {
      "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEFG"
    }
  }],
  "DefaultRootObject": "index.html",
  "CustomErrorResponses": [{
    "ErrorCode": 404,
    "ResponsePagePath": "/index.html",
    "ResponseCode": "200",
    "ErrorCachingMinTTL": 300
  }],
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-activation-manager",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true
  }
}
```

## Step 4: API Gateway Configuration

### Terraform Configuration
```hcl
resource "aws_api_gateway_rest_api" "activation_api" {
  name = "activation-manager-api"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "prod" {
  rest_api_id = aws_api_gateway_rest_api.activation_api.id
  stage_name  = "prod"
  
  lifecycle {
    create_before_destroy = true
  }
}

# Rate limiting
resource "aws_api_gateway_usage_plan" "standard" {
  name = "standard-usage-plan"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.activation_api.id
    stage  = aws_api_gateway_deployment.prod.stage_name
  }
  
  throttle_settings {
    rate_limit  = 1000
    burst_limit = 2000
  }
  
  quota_settings {
    limit  = 100000
    period = "DAY"
  }
}
```

## Step 5: Security Implementation

### API Authentication
```python
# activation_manager/api/auth.py
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import check_password_hash
import boto3

jwt = JWTManager()

@app.route('/api/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    # Verify against Cognito or your auth service
    # ...
    
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

@app.route('/api/nl/process', methods=['POST'])
@jwt_required()
def process_protected():
    # Your existing process logic
    pass
```

### Environment Configuration
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@host:5432/activation_manager
REDIS_URL=redis://redis-cluster.aws.com:6379
JWT_SECRET_KEY=your-secret-key
AWS_REGION=us-east-1
SENTRY_DSN=https://your-sentry-dsn
```

## Step 6: Monitoring and Logging

### CloudWatch Alarms
```python
# terraform/monitoring.tf
resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "activation-api-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors API errors"
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "activation-manager"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "activation-api"],
            [".", "MemoryUtilization", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "ECS Resource Utilization"
        }
      }
    ]
  })
}
```

## Step 7: CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python -m pytest

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build and push Docker image
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t activation-api .
          docker tag activation-api:latest $ECR_REGISTRY/activation-api:latest
          docker push $ECR_REGISTRY/activation-api:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service --cluster production --service activation-api --force-new-deployment

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build React app
        run: |
          cd audience-manager
          npm ci
          npm run build
      
      - name: Deploy to S3
        run: |
          aws s3 sync audience-manager/build/ s3://activation-manager-frontend/
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_ID }} --paths "/*"
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_postal_code ON consumer_data(postal_code);
CREATE INDEX idx_prizm_segment ON consumer_data(prizm_segment);

-- Create materialized view for faster aggregations
CREATE MATERIALIZED VIEW mv_segment_summary AS
SELECT 
    prizm_segment,
    COUNT(*) as count,
    AVG(latitude) as avg_lat,
    AVG(longitude) as avg_lng
FROM consumer_data
GROUP BY prizm_segment;

-- Refresh periodically
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_segment_summary;
END;
$$ LANGUAGE plpgsql;
```

### 2. Redis Caching
```python
# activation_manager/api/cache.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(os.environ.get('REDIS_URL'))

def cache_result(expiration=3600):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=7200)
def analyze_request(user_request):
    # Your expensive operation
    pass
```

## Disaster Recovery

### Backup Strategy
```bash
# Daily RDS snapshots
aws rds create-db-snapshot \
  --db-instance-identifier activation-manager-prod \
  --db-snapshot-identifier activation-manager-$(date +%Y%m%d)

# S3 cross-region replication
aws s3api put-bucket-replication \
  --bucket activation-manager-frontend \
  --replication-configuration file://replication.json
```

### Multi-Region Failover
- Use Route 53 health checks
- Maintain standby RDS in another region
- Use S3 cross-region replication
- Document runbooks for failover procedures

## Cost Optimization

1. **Use Reserved Instances** for predictable workloads
2. **Implement auto-scaling** for ECS tasks
3. **Use S3 lifecycle policies** for old data
4. **Enable CloudFront compression**
5. **Use Parameter Store** instead of Secrets Manager for non-sensitive config
6. **Monitor with Cost Explorer** and set billing alerts

## Production Checklist

- [ ] SSL certificates configured
- [ ] Database backups automated
- [ ] Monitoring alerts set up
- [ ] Log aggregation configured
- [ ] Security scan completed
- [ ] Load testing performed
- [ ] Disaster recovery tested
- [ ] Documentation updated
- [ ] Team trained on runbooks
- [ ] Support rotation established

---
*Last Updated: May 25, 2025*