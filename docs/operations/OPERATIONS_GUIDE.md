# Operations Guide

This guide covers monitoring, maintenance, troubleshooting, and operational procedures for the Activation Manager application.

## Table of Contents
1. [Monitoring](#monitoring)
2. [Maintenance Procedures](#maintenance-procedures)
3. [Troubleshooting](#troubleshooting)
4. [Performance Optimization](#performance-optimization)
5. [Security Operations](#security-operations)
6. [Incident Response](#incident-response)
7. [Backup and Recovery](#backup-and-recovery)
8. [Cost Management](#cost-management)

## Monitoring

### Health Checks

#### Automated Monitoring Script
```bash
# Run monitoring script
./monitor-deployment.sh
```

#### Manual Health Checks
```bash
# Check frontend
curl -I https://tobermory.ai

# Check API health
curl https://api.tobermory.ai/health

# With authentication
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" https://api.tobermory.ai/health
```

### Real-time Logs

#### Stream Logs
```bash
# Frontend logs
gcloud beta run services logs tail audience-manager --region us-central1

# Backend logs
gcloud beta run services logs tail audience-manager-api --region us-central1

# Both services
gcloud logging tail "resource.type=cloud_run_revision" --format=json
```

#### Query Historical Logs
```bash
# Last hour of errors
gcloud logging read "severity>=ERROR AND timestamp>=\"$(date -u -Iseconds -d '1 hour ago')\"" \
    --format=json --limit=50

# Specific service logs
gcloud logs read --service=audience-manager-api --limit=100

# Search for specific patterns
gcloud logging read "textPayload:\"500\" OR textPayload:\"ERROR\"" --limit=50
```

### Metrics and Dashboards

#### Cloud Console Monitoring
1. Navigate to: https://console.cloud.google.com/monitoring
2. Key metrics to monitor:
   - Request count
   - Request latency
   - Error rate
   - Container CPU utilization
   - Container memory utilization
   - Cold start frequency

#### Custom Alerts
```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-filter='
        resource.type="cloud_run_revision"
        AND metric.type="run.googleapis.com/request_count"
        AND metric.labels.response_code_class="5xx"'
```

### Application Monitoring

#### Key Metrics to Track
1. **Performance Metrics**
   - Page load time
   - API response time
   - Time to interactive
   - First contentful paint

2. **Business Metrics**
   - Active users
   - Audiences created
   - API calls per user
   - Export frequency

3. **Error Metrics**
   - JavaScript errors
   - API error rate
   - Failed logins
   - Timeout errors

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- [ ] Check monitoring dashboard
- [ ] Review error logs
- [ ] Verify SSL certificate status
- [ ] Check service health

#### Weekly
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Analyze usage patterns
- [ ] Test backup procedures

#### Monthly
- [ ] Update dependencies
- [ ] Review and optimize costs
- [ ] Security audit
- [ ] Performance testing

### Deployment Procedures

#### Standard Deployment
```bash
# Backend deployment
cd simple-backend
gcloud run deploy audience-manager-api \
    --source . \
    --region us-central1 \
    --no-traffic

# Test new revision
REVISION_URL=$(gcloud run revisions describe \
    audience-manager-api-LATEST \
    --region us-central1 \
    --format 'value(status.url)')

curl $REVISION_URL/health

# Promote to production
gcloud run services update-traffic audience-manager-api \
    --to-latest \
    --region us-central1
```

#### Rollback Procedure
```bash
# List revisions
gcloud run revisions list \
    --service audience-manager-api \
    --region us-central1

# Rollback to previous revision
gcloud run services update-traffic audience-manager-api \
    --to-revisions=audience-manager-api-00001-abc=100 \
    --region us-central1
```

### SSL Certificate Management

#### Check Certificate Status
```bash
# Monitor certificate
gcloud beta run domain-mappings describe \
    --domain tobermory.ai \
    --region us-central1

# Check expiration
echo | openssl s_client -servername tobermory.ai \
    -connect tobermory.ai:443 2>/dev/null | \
    openssl x509 -noout -dates
```

Google manages SSL certificate renewal automatically. No manual intervention required.

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Unavailable (503)
**Symptoms**: Application returns 503 errors
**Diagnosis**:
```bash
# Check service status
gcloud run services describe audience-manager --region us-central1

# Check for deployment issues
gcloud builds list --limit=5
```
**Solutions**:
- Check if service has scaled to zero
- Verify container is healthy
- Check resource limits

#### 2. Authentication Errors
**Symptoms**: Users cannot login or get 401 errors
**Diagnosis**:
```bash
# Check backend logs
gcloud logs read --service=audience-manager-api \
    --filter="textPayload:auth" --limit=20

# Test auth endpoint
curl -X POST https://api.tobermory.ai/api/auth/status
```
**Solutions**:
- Verify CORS configuration
- Check session secret is set
- Ensure cookies are enabled

#### 3. Slow Performance
**Symptoms**: Long load times, timeouts
**Diagnosis**:
```bash
# Check metrics
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/request_latencies"'

# Check cold starts
gcloud logs read --service=audience-manager \
    --filter="textPayload:\"Cold start\""
```
**Solutions**:
- Increase minimum instances
- Optimize container size
- Enable CDN caching

#### 4. Domain Not Accessible
**Symptoms**: Custom domain returns errors
**Diagnosis**:
```bash
# Check DNS
dig tobermory.ai

# Check domain mapping
gcloud beta run domain-mappings list --region us-central1
```
**Solutions**:
- Verify DNS records
- Check SSL certificate status
- Ensure Cloud Run service is running

### Debug Commands

#### Service Inspection
```bash
# Detailed service info
gcloud run services describe audience-manager \
    --region us-central1 \
    --format=export

# List all revisions
gcloud run revisions list \
    --service audience-manager \
    --region us-central1

# Check IAM policies
gcloud run services get-iam-policy audience-manager \
    --region us-central1
```

#### Container Debugging
```bash
# Get container logs
gcloud logging read \
    "resource.type=cloud_run_revision AND \
     resource.labels.service_name=audience-manager-api" \
    --limit=100

# Check container configuration
gcloud run services describe audience-manager-api \
    --region us-central1 \
    --format="get(spec.template.spec.containers[0])"
```

## Performance Optimization

### Frontend Optimization

#### 1. Enable Cloudflare Caching
- Set appropriate cache headers
- Enable Auto Minify
- Use Cloudflare CDN

#### 2. Optimize Bundle Size
```bash
# Analyze bundle
npm run build
npm run analyze

# Key optimizations:
- Code splitting
- Tree shaking
- Lazy loading
```

#### 3. Image Optimization
- Use WebP format
- Implement responsive images
- Lazy load images

### Backend Optimization

#### 1. Minimize Cold Starts
```bash
# Set minimum instances
gcloud run services update audience-manager-api \
    --min-instances=1 \
    --region us-central1
```

#### 2. Optimize Container
- Use multi-stage builds
- Minimize image size
- Cache dependencies

#### 3. Database Optimization (Future)
- Connection pooling
- Query optimization
- Caching layer

### Scaling Configuration

#### Auto-scaling Settings
```bash
# Update scaling parameters
gcloud run services update audience-manager \
    --max-instances=20 \
    --concurrency=1000 \
    --cpu=2 \
    --memory=1Gi \
    --region us-central1
```

## Security Operations

### Security Monitoring

#### 1. Access Logs
```bash
# Monitor access patterns
gcloud logging read \
    "protoPayload.requestMethod=\"POST\" AND \
     protoPayload.resource.labels.service_name=\"audience-manager-api\"" \
    --limit=100
```

#### 2. Failed Login Attempts
```bash
# Track failed logins
gcloud logs read \
    --service=audience-manager-api \
    --filter="textPayload:\"Failed login\"" \
    --limit=50
```

### Security Updates

#### 1. Dependency Updates
```bash
# Backend
cd simple-backend
pip list --outdated
pip install --upgrade -r requirements.txt

# Frontend
cd audience-manager
npm outdated
npm update
```

#### 2. Container Updates
```bash
# Rebuild with latest base images
docker build --no-cache -t audience-manager .
```

### Access Control

#### 1. IAM Management
```bash
# List current bindings
gcloud projects get-iam-policy feisty-catcher-461000-g2

# Grant access
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="user:email@example.com" \
    --role="roles/run.developer"
```

#### 2. Service Account Management
```bash
# Create service account
gcloud iam service-accounts create audience-manager-sa \
    --display-name="Audience Manager Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding feisty-catcher-461000-g2 \
    --member="serviceAccount:audience-manager-sa@feisty-catcher-461000-g2.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

## Incident Response

### Incident Response Procedure

#### 1. Detection
- Automated alerts
- User reports
- Monitoring dashboards

#### 2. Assessment
```bash
# Quick health check
./monitor-deployment.sh

# Check all services
for service in audience-manager audience-manager-api; do
  echo "Checking $service..."
  gcloud run services describe $service \
    --region us-central1 \
    --format="table(status.conditions.type,status.conditions.status)"
done
```

#### 3. Mitigation
- Immediate: Scale up resources
- Short-term: Rollback if needed
- Long-term: Fix root cause

#### 4. Communication
- Update status page
- Notify stakeholders
- Document timeline

#### 5. Post-Mortem
- Root cause analysis
- Lessons learned
- Action items

### Emergency Procedures

#### Complete Service Restart
```bash
# Force restart all instances
for service in audience-manager audience-manager-api; do
  gcloud run services update $service \
    --region us-central1 \
    --clear-env-vars=DUMMY \
    --update-env-vars=DUMMY=1
done
```

#### Emergency Scaling
```bash
# Scale up immediately
gcloud run services update audience-manager-api \
    --min-instances=5 \
    --max-instances=50 \
    --region us-central1
```

## Backup and Recovery

### Current State
- **Code**: Stored in Git
- **Configuration**: Version controlled
- **Data**: Currently stateless

### Future Backup Strategy

#### Database Backups (When Implemented)
```bash
# Cloud SQL automated backups
gcloud sql instances patch audience-manager-db \
    --backup-start-time=03:00 \
    --retained-backups-count=7 \
    --retained-transaction-log-days=7
```

#### Configuration Backup
```bash
# Export service configuration
gcloud run services export audience-manager \
    --region us-central1 \
    --format-export > audience-manager-config.yaml

# Export domain mappings
gcloud beta run domain-mappings list \
    --region us-central1 \
    --format=export > domain-mappings.yaml
```

### Recovery Procedures

#### Service Recovery
```bash
# Restore from configuration
gcloud run services replace audience-manager-config.yaml \
    --region us-central1
```

#### Data Recovery (Future)
```bash
# Restore Cloud SQL from backup
gcloud sql backups restore BACKUP_ID \
    --restore-instance=audience-manager-db
```

## Cost Management

### Cost Monitoring

#### View Current Costs
```bash
# Monthly cost forecast
gcloud billing budgets list

# Detailed cost breakdown
# Visit: https://console.cloud.google.com/billing
```

### Cost Optimization Strategies

#### 1. Right-size Resources
```bash
# Analyze usage
gcloud monitoring read \
    --filter='metric.type="run.googleapis.com/container/cpu/utilizations"' \
    --format=table

# Adjust resources
gcloud run services update audience-manager-api \
    --memory=256Mi \
    --cpu=1 \
    --region us-central1
```

#### 2. Optimize Scaling
```bash
# Set appropriate limits
gcloud run services update audience-manager \
    --max-instances=5 \
    --min-instances=0 \
    --region us-central1
```

#### 3. Enable Cost Alerts
```bash
# Create budget alert
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Audience Manager Monthly Budget" \
    --budget-amount=100 \
    --threshold-rule=percent=0.9
```

### Cost Breakdown (Estimated)
- Cloud Run: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Requests: $0.40/million requests
- Bandwidth: $0.12/GB

Typical monthly cost: $5-20 for moderate usage

## Appendix

### Useful Scripts

#### Health Check Loop
```bash
#!/bin/bash
while true; do
    curl -s https://api.tobermory.ai/health | jq .
    sleep 60
done
```

#### Log Monitor
```bash
#!/bin/bash
gcloud logging tail \
    "severity>=WARNING AND \
     resource.type=cloud_run_revision" \
    --format="value(timestamp,severity,textPayload)"
```

#### Cost Monitor
```bash
#!/bin/bash
gcloud billing accounts list
gcloud beta billing accounts get-spending-info ACCOUNT_ID \
    --format="table(costAmount,creditAmount,currency)"
```