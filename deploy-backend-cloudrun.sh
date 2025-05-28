#!/bin/bash

# GCP Cloud Run Backend Deployment Script
# Deploys the Python backend API to Cloud Run

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
SERVICE_NAME="audience-manager-api"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${SERVICE_NAME}"

echo -e "${BLUE}=== Backend API Cloud Run Deployment ===${NC}"
echo -e "Project: ${YELLOW}$PROJECT_ID${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo -e "Service: ${YELLOW}$SERVICE_NAME${NC}"
echo ""

# Create API directory if it doesn't exist
mkdir -p api-deploy
cd api-deploy

# Copy necessary files
echo -e "${YELLOW}Preparing deployment files...${NC}"
cp -r ../src/api .
cp ../requirements.txt .

# Create a simple Flask app wrapper
echo -e "${YELLOW}Creating main.py...${NC}"
cat > main.py << 'EOF'
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Sample data storage (in production, use a real database)
audiences = []
segments = []

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "audience-manager-api"})

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    session_id = f"session_{random.randint(1000, 9999)}"
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST'])
def process_workflow():
    data = request.json
    action = data.get('action')
    
    if action == 'process':
        # Simulate variable suggestion
        return jsonify({
            "status": "variables_suggested",
            "suggested_variables": {
                "demographic": [
                    {"code": "age", "description": "Age Range", "type": "demographic", "relevance_score": 0.9},
                    {"code": "income", "description": "Income Level", "type": "demographic", "relevance_score": 0.85},
                    {"code": "location", "description": "Geographic Location", "type": "demographic", "relevance_score": 0.8}
                ],
                "behavioral": [
                    {"code": "purchase_freq", "description": "Purchase Frequency", "type": "behavioral", "relevance_score": 0.75},
                    {"code": "engagement", "description": "Engagement Level", "type": "behavioral", "relevance_score": 0.7}
                ]
            }
        })
    elif action == 'confirm':
        # Simulate segment creation
        segments = []
        for i in range(4):
            segments.append({
                "group_id": i,
                "size": random.randint(10000, 50000),
                "size_percentage": random.uniform(5, 10),
                "name": f"Segment {i+1}",
                "dominantTraits": ["High Value", "Engaged", "Urban"]
            })
        
        return jsonify({
            "status": "complete",
            "segments": segments,
            "audience_id": f"aud_{random.randint(1000, 9999)}"
        })
    
    return jsonify({"status": "unknown_action"})

@app.route('/api/audiences', methods=['GET', 'POST'])
def handle_audiences():
    if request.method == 'GET':
        return jsonify(audiences)
    elif request.method == 'POST':
        audience = request.json
        audience['id'] = f"aud_{random.randint(1000, 9999)}"
        audience['createdAt'] = datetime.now().isoformat()
        audiences.append(audience)
        return jsonify(audience), 201

@app.route('/api/export/<audience_id>', methods=['GET'])
def export_audience(audience_id):
    # Simulate CSV export
    csv_content = "id,segment,size\n"
    for i in range(4):
        csv_content += f"{i},{audience_id}_segment_{i},{random.randint(1000, 5000)}\n"
    
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=audience_{audience_id}.csv'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

# Create requirements.txt for the API
echo -e "${YELLOW}Creating requirements.txt...${NC}"
cat > requirements.txt << 'EOF'
Flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
EOF

# Create Dockerfile
echo -e "${YELLOW}Creating Dockerfile...${NC}"
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
EOF

# Build and deploy
echo -e "${YELLOW}Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} .

echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

# Clean up
cd ..
rm -rf api-deploy

echo ""
echo -e "${GREEN}=== Backend Deployment Complete ===${NC}"
echo -e "${GREEN}API URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}Test the API:${NC}"
echo "curl ${SERVICE_URL}/health"
echo ""
echo -e "${YELLOW}Update your frontend .env:${NC}"
echo "REACT_APP_API_URL=${SERVICE_URL}"