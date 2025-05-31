#!/bin/bash

echo -e "\033[0;34m🚀 Deploying with App Engine Flexible Environment\033[0m"
echo -e "\033[1;33mThis approach may bypass Cloud Build staging issues\033[0m"

# Create deployment directory
DEPLOY_DIR="flex_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Create flexible environment app.yaml
cat > $DEPLOY_DIR/app.yaml << 'EOF'
runtime: python
env: flex

runtime_config:
  python_version: 3

# Flexible environment settings
resources:
  cpu: 1
  memory_gb: 1.5
  disk_size_gb: 10

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 2

# Environment variables
env_variables:
  FLASK_ENV: production
  ENVIRONMENT: production

handlers:
- url: /static
  static_dir: audience-manager/build/static
  secure: always

- url: /.*
  script: auto
  secure: always
EOF

# Copy essential files
echo -e "\033[1;33mCopying essential files...\033[0m"
cp main.py $DEPLOY_DIR/
cp backend_gcp.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/

# Copy activation_manager module (without large data files)
mkdir -p $DEPLOY_DIR/activation_manager/core
cp activation_manager/__init__.py $DEPLOY_DIR/activation_manager/
cp activation_manager/core/variable_selector.py $DEPLOY_DIR/activation_manager/core/
cp activation_manager/core/audience_builder.py $DEPLOY_DIR/activation_manager/core/
cp activation_manager/core/prizm_analyzer.py $DEPLOY_DIR/activation_manager/core/

# Copy minimal frontend build
if [ -d "audience-manager/build" ]; then
    echo -e "\033[1;33mCopying frontend build...\033[0m"
    mkdir -p $DEPLOY_DIR/audience-manager
    cp -r audience-manager/build $DEPLOY_DIR/audience-manager/
fi

# Create Dockerfile for flexible environment
cat > $DEPLOY_DIR/Dockerfile << 'EOF'
FROM gcr.io/google-appengine/python

# Create a virtualenv for dependencies
RUN virtualenv -p python3 /env

# Setting these environment variables are the same as running
# source /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add the application source code.
ADD . /app

# Run a WSGI server to serve the application. gunicorn must be
# declared as a dependency in requirements.txt.
CMD gunicorn -b :$PORT main:app
EOF

# Update requirements to include gunicorn
echo "gunicorn==21.2.0" >> $DEPLOY_DIR/requirements.txt

# Deploy
echo -e "\033[1;33mDeploying with flexible environment...\033[0m"
cd $DEPLOY_DIR
gcloud app deploy --quiet

if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Deployment successful!\033[0m"
    echo -e "\033[0;34mYour app is available at: https://feisty-catcher-461000-g2.nn.r.appspot.com\033[0m"
    cd ..
    rm -rf $DEPLOY_DIR
else
    echo -e "\033[0;31m❌ Deployment failed\033[0m"
    echo -e "\033[1;33mDeploy directory preserved at: $DEPLOY_DIR\033[0m"
fi