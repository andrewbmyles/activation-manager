#!/bin/bash

echo -e "\033[0;34m🚀 Deploying to Cloud Run (Alternative to App Engine)\033[0m"
echo -e "\033[1;33mCloud Run doesn't require staging bucket permissions\033[0m"

# Set variables
PROJECT_ID="feisty-catcher-461000-g2"
SERVICE_NAME="activation-manager"
REGION="us-central1"

# Create deployment directory
DEPLOY_DIR="cloudrun_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Create Dockerfile
cat > $DEPLOY_DIR/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for static files
RUN mkdir -p audience-manager/build/static

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
EOF

# Create main.py for Cloud Run
cat > $DEPLOY_DIR/main.py << 'EOF'
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])

# Serve static files
@app.route('/')
def serve_frontend():
    build_dir = 'audience-manager/build'
    if os.path.exists(os.path.join(build_dir, 'index.html')):
        return send_from_directory(build_dir, 'index.html')
    return jsonify({"message": "Activation Manager API", "status": "running"})

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('audience-manager/build/static', path)

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "activation-manager"})

# Variable picker endpoints
@app.route('/api/variable-picker/start', methods=['POST', 'OPTIONS'])
def start_variable_picker():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    query = data.get('query', '')
    
    # For now, return mock data
    return jsonify({
        "session_id": "cloud-run-session",
        "results": [
            {
                "code": "DEMO001",
                "name": f"Variable matching '{query}'",
                "description": "Demo variable from Cloud Run deployment",
                "relevance_score": 0.95
            }
        ],
        "total_results": 1,
        "query": query
    })

@app.route('/api/variable-picker/feedback', methods=['POST', 'OPTIONS'])
def variable_feedback():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({"status": "feedback received"})

@app.route('/api/variable-picker/select', methods=['POST', 'OPTIONS'])
def select_variable():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    return jsonify({
        "status": "variable selected",
        "variable_code": data.get('variable_code')
    })

# Natural language endpoint
@app.route('/api/nl/process', methods=['POST', 'OPTIONS'])
def process_nl():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    return jsonify({
        "query": data.get('query', ''),
        "audiences": [
            {
                "id": "cloud-run-audience",
                "name": "Demo Audience",
                "criteria": "age > 25"
            }
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

# Create requirements.txt
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
Flask==2.3.0
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Copy frontend build if exists
if [ -d "audience-manager/build" ]; then
    echo -e "\033[1;33mCopying frontend build...\033[0m"
    mkdir -p $DEPLOY_DIR/audience-manager
    cp -r audience-manager/build $DEPLOY_DIR/audience-manager/
fi

# Build and deploy to Cloud Run
echo -e "\033[1;33mBuilding container image...\033[0m"
cd $DEPLOY_DIR

# Build using Cloud Build (but for Cloud Run, not App Engine)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

if [ $? -eq 0 ]; then
    echo -e "\033[1;33mDeploying to Cloud Run...\033[0m"
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi
    
    if [ $? -eq 0 ]; then
        echo -e "\033[0;32m✅ Cloud Run deployment successful!\033[0m"
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
        echo -e "\033[0;34mYour app is available at: $SERVICE_URL\033[0m"
        cd ..
        rm -rf $DEPLOY_DIR
    else
        echo -e "\033[0;31m❌ Cloud Run deployment failed\033[0m"
    fi
else
    echo -e "\033[0;31m❌ Container build failed\033[0m"
    echo -e "\033[1;33mAlternative: Try deploying from source\033[0m"
    echo "gcloud run deploy $SERVICE_NAME --source . --region $REGION --allow-unauthenticated"
fi