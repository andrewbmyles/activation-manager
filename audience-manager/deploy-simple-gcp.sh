#!/bin/bash

# Simple GCP Cloud Run Deployment using Source Deploy
# This uses Cloud Run's built-in build capability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="feisty-catcher-461000-g2"
REGION="northamerica-northeast1"

echo -e "${BLUE}=== Simple GCP Cloud Run Deployment ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo ""

# Step 1: Deploy Backend API
echo -e "${BLUE}Step 1: Deploying Backend API${NC}"

# Create a simple backend directory
mkdir -p simple-backend
cd simple-backend

# Create a simple Flask API
cat > app.py << 'EOF'
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])

# In-memory storage for demo
sessions = {}
audiences = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    session_id = f"session_{random.randint(1000, 9999)}"
    sessions[session_id] = {"created": datetime.now().isoformat()}
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST'])
def process():
    data = request.json
    action = data.get('action')
    
    if action == 'process':
        return jsonify({
            "status": "variables_suggested",
            "suggested_variables": {
                "demographic": [
                    {"code": "age", "description": "Age Range", "type": "demographic", "relevance_score": 0.9},
                    {"code": "income", "description": "Income Level", "type": "demographic", "relevance_score": 0.85}
                ],
                "behavioral": [
                    {"code": "purchase", "description": "Purchase Behavior", "type": "behavioral", "relevance_score": 0.8}
                ]
            }
        })
    elif action == 'confirm':
        segments = []
        for i in range(4):
            segments.append({
                "group_id": i,
                "size": random.randint(10000, 50000),
                "size_percentage": random.uniform(5, 10),
                "name": f"Segment {i+1}"
            })
        return jsonify({
            "status": "complete",
            "segments": segments,
            "audience_id": f"aud_{random.randint(1000, 9999)}"
        })
    
    return jsonify({"status": "error", "message": "Unknown action"})

@app.route('/api/export/<audience_id>', methods=['GET'])
def export(audience_id):
    csv_data = "id,segment,size\n"
    for i in range(4):
        csv_data += f"{i},segment_{i},{random.randint(1000, 5000)}\n"
    
    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=audience_{audience_id}.csv'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Create Procfile for Cloud Run
cat > Procfile << 'EOF'
web: gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
EOF

# Deploy backend using source deploy
echo -e "${YELLOW}Deploying backend API...${NC}"
gcloud run deploy audience-manager-api \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe audience-manager-api --platform managed --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

# Go back to main directory
cd ..

# Step 2: Deploy Frontend
echo -e "${BLUE}Step 2: Deploying Frontend${NC}"

# Update environment file
cat > .env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
GENERATE_SOURCEMAP=false
EOF

# Build React app
echo -e "${YELLOW}Building React app...${NC}"
npm run build

# Create a simple static server
mkdir -p frontend-deploy
cp -r build/* frontend-deploy/

# Create a simple Node.js server for the frontend
cd frontend-deploy
cat > server.js << 'EOF'
const express = require('express');
const path = require('path');
const app = express();

// Serve static files
app.use(express.static('.'));

// Handle React routing
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'index.html'));
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
EOF

# Create package.json
cat > package.json << 'EOF'
{
  "name": "audience-manager-frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF

# Deploy frontend
echo -e "${YELLOW}Deploying frontend...${NC}"
gcloud run deploy audience-manager \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe audience-manager --platform managed --region ${REGION} --format 'value(status.url)')

# Cleanup
cd ..
rm -rf simple-backend frontend-deploy

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Frontend: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend API: ${BACKEND_URL}${NC}"
echo ""
echo -e "${BLUE}Test Commands:${NC}"
echo "# Test API health"
echo "curl ${BACKEND_URL}/health"
echo ""
echo "# View logs"
echo "gcloud run logs read --service audience-manager --region ${REGION}"
echo "gcloud run logs read --service audience-manager-api --region ${REGION}"