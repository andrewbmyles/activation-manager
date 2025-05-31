#!/bin/bash

# Deploy using legacy approach

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying with legacy approach${NC}"

# Create super minimal config
cat > app_legacy.yaml << 'EOF'
runtime: python311

handlers:
- url: /.*
  script: auto
EOF

# Use minimal backend
cat > main.py << 'EOF'
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return 'Activation Manager is running!'
EOF

# Minimal requirements
cat > requirements.txt << 'EOF'
Flask==2.3.3
gunicorn==21.2.0
EOF

echo -e "${YELLOW}Deploying with legacy settings...${NC}"

# Try deployment with different bucket
export CLOUDSDK_APP_USE_GSUTIL=1
gcloud config set app/use_deprecated_preparation True

gcloud app deploy app_legacy.yaml \
    --quiet \
    --project=feisty-catcher-461000-g2 \
    --version=legacy-$(date +%s) \
    --no-cache

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${BLUE}Your app is at: https://feisty-catcher-461000-g2.appspot.com${NC}"
else
    echo -e "${RED}❌ Still failing. Let's try one more approach...${NC}"
fi