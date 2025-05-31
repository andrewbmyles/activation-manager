#!/bin/bash

# Deploy to staging with unified search migration (0% rollout initially)
# This allows us to test the migration framework without affecting any users

set -e

echo "🚀 Deploying unified search to staging with 0% rollout..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Set environment variables for 0% rollout
export USE_UNIFIED_SEARCH=false
export UNIFIED_ROLLOUT_PERCENTAGE=0

# Update app.yaml with unified search environment variables
cat > app_staging_unified.yaml << EOF
runtime: python312
service: default

# Unified Search Migration Settings (0% rollout)
env_variables:
  USE_UNIFIED_SEARCH: "false"
  UNIFIED_ROLLOUT_PERCENTAGE: "0"
  DEMO_PASSWORD: "demo2024"
  GCS_BUCKET: "activation-manager-embeddings"

instance_class: F2

automatic_scaling:
  min_instances: 1
  max_instances: 5
  min_idle_instances: 1
  max_idle_instances: 1
  target_cpu_utilization: 0.75
  max_concurrent_requests: 20

handlers:
- url: /static
  static_dir: audience-manager/build/static
  secure: always

- url: /activation-manager/static
  static_dir: audience-manager/build/static
  secure: always

- url: /activation-manager
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
  secure: always

- url: /activation-manager/.*
  static_files: audience-manager/build/index.html
  upload: audience-manager/build/index.html
  secure: always

- url: /favicon.ico
  static_files: audience-manager/build/favicon.ico
  upload: audience-manager/build/favicon.ico
  secure: always

- url: /manifest.json
  static_files: audience-manager/build/manifest.json
  upload: audience-manager/build/manifest.json
  secure: always

- url: /api/.*
  script: auto
  secure: always

- url: /health
  script: auto
  secure: always

- url: /_ah/.*
  script: auto

- url: /.*
  static_files: tobermory-web/build/index.html
  upload: tobermory-web/build/index.html
  secure: always
EOF

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  - Service: default (staging)"
echo "  - USE_UNIFIED_SEARCH: false"
echo "  - UNIFIED_ROLLOUT_PERCENTAGE: 0%"
echo "  - Migration endpoints enabled"

# Build frontend if needed
if [ ! -d "audience-manager/build" ]; then
    echo -e "${YELLOW}📦 Building frontend...${NC}"
    cd audience-manager
    npm install
    npm run build
    cd ..
fi

# Deploy to staging
echo -e "${GREEN}☁️  Deploying to staging...${NC}"
gcloud app deploy app_staging_unified.yaml \
    --project=feisty-catcher-461000-g2 \
    --quiet \
    --version=stg-unified-$(date +%Y%m%d-%H%M%S)

# Test deployment
echo -e "${GREEN}🧪 Testing deployment...${NC}"

# Wait for deployment to be ready
sleep 10

# Test migration status endpoint
echo -e "${YELLOW}Testing migration status endpoint...${NC}"
curl -s https://feisty-catcher-461000-g2.uc.r.appspot.com/api/search/migration/status | python3 -m json.tool

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Migration endpoints:"
echo "  - Status: https://feisty-catcher-461000-g2.uc.r.appspot.com/api/search/migration/status"
echo "  - Test routing: POST https://feisty-catcher-461000-g2.uc.r.appspot.com/api/search/migration/test"
echo ""
echo "🔄 To increase rollout percentage:"
echo "  1. Update UNIFIED_ROLLOUT_PERCENTAGE in app.yaml"
echo "  2. Redeploy with: gcloud app deploy app_staging_unified.yaml"
echo ""
echo "📈 Monitor performance:"
echo "  - Check logs: gcloud app logs tail -s default"
echo "  - Look for AB_TEST_RESULT entries to compare implementations"