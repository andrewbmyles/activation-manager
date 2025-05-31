# Vercel Deployment Guide

## Overview
This guide covers deploying the Activation Manager to Vercel with both frontend (React) and backend (Python API) components.

## Prerequisites
- Vercel account
- Git repository
- Node.js 18+ installed locally
- Python 3.11+ for local testing

## Project Structure
```
activation-manager/
├── audience-manager/          # React frontend
│   ├── src/                  # React components
│   ├── public/               # Static assets
│   ├── api/                  # Serverless functions
│   │   └── index.py         # Python API endpoint
│   ├── package.json         # Node dependencies
│   ├── requirements.txt     # Python dependencies
│   └── vercel.json         # Vercel configuration
└── activation_manager/       # Python backend
    ├── api/                 # API modules
    ├── core/                # Core logic
    └── config/              # Configuration
```

## Configuration

### Environment Variables
Set these in your Vercel project settings:

```bash
# API Configuration
SYNTHETIC_DATA_PATH=/var/task/data/synthetic_consumer_data_100000.csv
API_DEBUG=false

# Optional: External services
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
```

### Data Handling
Due to the large dataset (1.7GB), we recommend:

1. **Option 1: Use sampling in production**
   - Modify the API to use a smaller sample
   - Store full dataset in external storage (S3, etc.)

2. **Option 2: Pre-process data**
   - Create aggregated datasets
   - Store in a database service

3. **Option 3: Edge caching**
   - Use Vercel's edge network for caching
   - Implement smart data fetching

## Deployment Steps

### 1. Prepare the Frontend
```bash
cd audience-manager
npm install
npm run build
```

### 2. Update API Endpoint
In `src/components/EnhancedNLAudienceBuilder.tsx`, update the API URL:
```typescript
const API_URL = process.env.REACT_APP_API_URL || '/api';
```

### 3. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts to link to your project
```

### 4. Configure Build Settings
In Vercel dashboard:
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 5. Test Deployment
Visit your Vercel URL and test:
1. Natural language query input
2. Variable selection
3. Audience segmentation
4. CSV export
5. Distribution simulation

## Performance Optimization

### Frontend
- Enable compression
- Use CDN for static assets
- Implement lazy loading
- Cache API responses

### Backend
- Use serverless function caching
- Implement data pagination
- Optimize clustering for smaller datasets
- Use edge functions for light operations

## Monitoring

### Vercel Analytics
- Enable Web Analytics
- Monitor function execution times
- Track error rates

### Custom Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Processing request: {request_id}")
```

## Troubleshooting

### Common Issues

1. **Function Timeout**
   - Increase timeout in vercel.json
   - Implement async processing
   - Use smaller data samples

2. **Memory Limits**
   - Current limit: 3008MB
   - Optimize data loading
   - Use streaming for large exports

3. **Cold Starts**
   - Pre-warm functions
   - Use edge functions
   - Optimize imports

### Debug Mode
Enable detailed logging:
```python
if os.getenv('API_DEBUG') == 'true':
    app.config['DEBUG'] = True
```

## Security Considerations

1. **API Authentication**
   - Implement API keys
   - Use Vercel's built-in auth
   - Add rate limiting

2. **Data Protection**
   - Don't expose raw data
   - Implement access controls
   - Use HTTPS only

3. **Input Validation**
   - Sanitize user inputs
   - Limit query complexity
   - Validate file uploads

## Cost Optimization

1. **Function Invocations**
   - Cache common queries
   - Batch operations
   - Use static generation where possible

2. **Bandwidth**
   - Compress responses
   - Paginate large datasets
   - Use efficient data formats

3. **Compute Time**
   - Optimize algorithms
   - Pre-compute when possible
   - Use appropriate function size

## Next Steps

1. Set up continuous deployment from GitHub
2. Configure custom domain
3. Implement monitoring and alerts
4. Add A/B testing capabilities
5. Set up staging environment

## Support

For issues or questions:
- Check Vercel documentation
- Review function logs
- Contact development team