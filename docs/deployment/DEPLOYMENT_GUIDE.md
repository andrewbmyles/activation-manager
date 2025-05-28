# Deployment Guide

This guide covers the complete deployment process for the Activation Manager application on Google Cloud Platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Custom Domain Configuration](#custom-domain-configuration)
6. [Authentication Setup](#authentication-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- Google Cloud SDK (`gcloud` CLI)
- Node.js 18+ and npm
- Python 3.11+
- Git
- Domain name (for custom domain setup)

### GCP Requirements
- Active Google Cloud Project
- Billing enabled
- Required APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Artifact Registry API

### Local Setup
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize gcloud
gcloud init

# Set project
gcloud config set project YOUR_PROJECT_ID
```

## Initial Setup

### 1. Clone Repository
```bash
git clone [repository-url]
cd audience-manager
```

### 2. Install Dependencies
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
npm install
```

### 3. Environment Configuration
Create `.env.production` file:
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

## Backend Deployment

### Simple Backend (Flask with Authentication)

The backend is located in `simple-backend/` and includes:
- Flask REST API
- Session-based authentication
- CORS configuration
- Health check endpoint

#### Deploy Command
```bash
cd simple-backend
gcloud run deploy audience-manager-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "SECRET_KEY=$(openssl rand -hex 32)"
```

#### Verify Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe audience-manager-api \
    --region us-central1 \
    --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health
```

## Frontend Deployment

### Build React Application
```bash
cd audience-manager
npm run build
```

### Deploy to Cloud Run
```bash
# Create deployment directory
mkdir -p frontend-deploy
cp -r build/* frontend-deploy/

# Create server configuration
cat > frontend-deploy/package.json << EOF
{
  "name": "audience-manager-frontend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF

# Create Express server
cat > frontend-deploy/server.js << EOF
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 8080;
app.use(express.static(path.join(__dirname)));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});
app.listen(PORT, () => {
  console.log(\`Server is running on port \${PORT}\`);
});
EOF

# Deploy
cd frontend-deploy
gcloud run deploy audience-manager \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10

# Cleanup
cd ..
rm -rf frontend-deploy
```

## Custom Domain Configuration

### 1. Verify Domain Ownership
```bash
# Check if domain is verified
gcloud domains list-user-verified

# If not verified, visit:
# https://console.cloud.google.com/apis/credentials/domainverification
```

### 2. Create Domain Mappings
```bash
# Map frontend domain
gcloud beta run domain-mappings create \
    --service audience-manager \
    --domain yourdomain.com \
    --region us-central1

# Map API subdomain
gcloud beta run domain-mappings create \
    --service audience-manager-api \
    --domain api.yourdomain.com \
    --region us-central1
```

### 3. Configure DNS Records

#### For Cloudflare:
1. Set SSL/TLS to "Full"
2. Disable proxy (gray cloud) initially
3. Add records:

**Frontend (root domain):**
- Type: A, Name: @, Value: 216.239.32.21
- Type: A, Name: @, Value: 216.239.34.21
- Type: A, Name: @, Value: 216.239.36.21
- Type: A, Name: @, Value: 216.239.38.21
- Type: AAAA, Name: @, Value: 2001:4860:4802:32::15
- Type: AAAA, Name: @, Value: 2001:4860:4802:34::15
- Type: AAAA, Name: @, Value: 2001:4860:4802:36::15
- Type: AAAA, Name: @, Value: 2001:4860:4802:38::15

**API (subdomain):**
- Type: CNAME, Name: api, Value: ghs.googlehosted.com.

### 4. Monitor SSL Certificate Provisioning
```bash
# Check status
gcloud beta run domain-mappings describe \
    --domain yourdomain.com \
    --region us-central1

# Use monitoring script
./monitor-deployment.sh
```

## Authentication Setup

### Backend Authentication
The backend uses Flask-Session with secure password hashing:

```python
# User storage (in production, use database)
USERS = {
    'user@example.com': generate_password_hash('password')
}

# Login endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in USERS and check_password_hash(USERS[email], password):
        session['user'] = email
        return jsonify({'success': True, 'user': email})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
```

### Frontend Authentication
React components handle authentication state:

```jsx
// App.tsx
const [user, setUser] = useState(null);

useEffect(() => {
  checkAuthStatus();
}, []);

const checkAuthStatus = async () => {
  const response = await fetch(`${API_URL}/api/auth/status`);
  const data = await response.json();
  if (data.authenticated) {
    setUser(data.user);
  }
};
```

### Adding New Users
Currently hardcoded in `simple-backend/app.py`. To add users:

1. Edit the USERS dictionary
2. Hash passwords with `generate_password_hash()`
3. Redeploy backend

## Monitoring and Maintenance

### Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend status
curl https://yourdomain.com
```

### View Logs
```bash
# Backend logs
gcloud logs read --service=audience-manager-api --limit=50

# Frontend logs
gcloud logs read --service=audience-manager --limit=50

# Stream logs
gcloud beta run services logs tail audience-manager-api
```

### Monitoring Script
Use the provided monitoring script:
```bash
./monitor-deployment.sh
```

### Cloud Console
Monitor services at:
https://console.cloud.google.com/run?project=YOUR_PROJECT_ID

## Troubleshooting

### Common Issues

#### 1. SSL Certificate Pending
- **Symptom**: Domain not accessible, SSL pending
- **Solution**: 
  - Verify DNS records are correct
  - Ensure Cloudflare proxy is disabled
  - Wait up to 24 hours for provisioning

#### 2. Authentication Errors
- **Symptom**: 401 errors on API calls
- **Solution**:
  - Check CORS configuration
  - Verify session secret is set
  - Ensure credentials are correct

#### 3. Deployment Failures
- **Symptom**: Build or deployment errors
- **Solution**:
  - Check build logs: `gcloud builds list`
  - Verify permissions
  - Ensure all files are included

#### 4. Domain Mapping Errors
- **Symptom**: Domain mapping creation fails
- **Solution**:
  - Use us-central1 region (domain mappings not supported in all regions)
  - Verify domain ownership
  - Check organization policies

### Debug Commands
```bash
# Check service status
gcloud run services describe audience-manager --region us-central1

# List domain mappings
gcloud beta run domain-mappings list --region us-central1

# Check permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Test with authentication token
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" https://api.yourdomain.com/health
```

## Security Considerations

1. **Environment Variables**: Use Secret Manager for production
2. **CORS**: Restrict to specific domains in production
3. **Authentication**: Implement proper user management system
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Implement rate limiting for API endpoints

## Cost Optimization

1. **Auto-scaling**: Set appropriate min/max instances
2. **Memory**: Use minimum required memory
3. **Cold Starts**: Keep one instance warm if needed
4. **Monitoring**: Set up billing alerts

## Next Steps

1. **Database Integration**: Replace in-memory storage with Cloud SQL
2. **CI/CD Pipeline**: Set up Cloud Build triggers
3. **Enhanced Security**: Implement OAuth or JWT tokens
4. **Monitoring**: Add application performance monitoring
5. **Backup Strategy**: Implement data backup procedures