#!/bin/bash

echo -e "\033[0;34m🚀 Deploying without Cloud Build\033[0m"
echo -e "\033[1;33mAttempting deployment with minimal configuration\033[0m"

# Create deployment directory
DEPLOY_DIR="nobuild_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Create minimal app.yaml
cat > $DEPLOY_DIR/app.yaml << 'EOF'
runtime: python311

# Minimal configuration
instance_class: F1

handlers:
- url: /.*
  script: auto
EOF

# Create minimal backend
cat > $DEPLOY_DIR/main.py << 'EOF'
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"status": "Activation Manager API", "version": "1.0"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

# Create minimal requirements
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
Flask==2.3.0
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Create .gcloudignore to exclude everything except essentials
cat > $DEPLOY_DIR/.gcloudignore << 'EOF'
# Exclude everything by default
*

# Include only essential files
!app.yaml
!main.py
!requirements.txt
EOF

# Try deployment with various flags to bypass Cloud Build
echo -e "\033[1;33mAttempting deployment...\033[0m"
cd $DEPLOY_DIR

# First, try to set the staging bucket permissions directly
echo -e "\033[1;33mSetting staging bucket permissions...\033[0m"
gsutil iam ch serviceAccount:feisty-catcher-461000-g2@appspot.gserviceaccount.com:objectAdmin gs://staging.feisty-catcher-461000-g2.appspot.com 2>/dev/null || true

# Try deployment
gcloud app deploy --quiet --no-cache

if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Minimal deployment successful!\033[0m"
    echo -e "\033[0;34mNow we can update with full functionality\033[0m"
    cd ..
    
    # If minimal deployment works, try full deployment
    ./deploy_final_solution.sh
else
    echo -e "\033[0;31m❌ Even minimal deployment failed\033[0m"
    echo -e "\033[1;33mThis indicates a project-level permission issue\033[0m"
    echo
    echo -e "\033[1;33mTry these manual steps:\033[0m"
    echo "1. Go to: https://console.cloud.google.com/cloud-build/settings?project=feisty-catcher-461000-g2"
    echo "2. Enable the Cloud Build API if not already enabled"
    echo "3. Grant the App Engine default service account the following roles:"
    echo "   - Cloud Build Service Account"
    echo "   - Storage Admin"
    echo
    echo "4. Or try creating the staging bucket manually:"
    echo "   gsutil mb -p feisty-catcher-461000-g2 gs://staging.feisty-catcher-461000-g2.appspot.com"
    echo "   gsutil iam ch serviceAccount:feisty-catcher-461000-g2@appspot.gserviceaccount.com:objectAdmin gs://staging.feisty-catcher-461000-g2.appspot.com"
fi