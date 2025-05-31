# Audience Manager Backend API

This is the CORS-enabled backend for the Audience Manager application, designed to run on Google Cloud Run.

## Features

- ✅ CORS properly configured for Vercel deployments
- ✅ Health check endpoint for monitoring
- ✅ Natural Language processing endpoints
- ✅ Audience management CRUD operations
- ✅ CSV export functionality
- ✅ Optional authentication support

## CORS Configuration

The backend is configured to accept requests from:
- `https://audience-manager.vercel.app` (production)
- `https://audience-manager-*.vercel.app` (preview deployments)
- `http://localhost:3000` (local development)

## Endpoints

- `GET /health` - Health check
- `GET /api` - API information
- `POST /api/nl/start_session` - Start NL session
- `POST /api/nl/process` - Process NL workflow
- `GET/POST /api/audiences` - Manage audiences
- `GET /api/export/<audience_id>` - Export audience as CSV

## Deployment

Run the deployment script from the parent directory:
```bash
./deploy-backend-cors.sh
```

## Testing CORS

Test that CORS is working properly:
```bash
# Replace with your actual Cloud Run URL
API_URL="https://audience-manager-api-xxxxx.run.app"

# Test preflight request
curl -X OPTIONS $API_URL/api/nl/start_session \
  -H "Origin: https://audience-manager.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" -v
```

## Local Development

To run locally:
```bash
cd gcp-backend
pip install -r requirements.txt
python main.py
```

The server will start on http://localhost:8080