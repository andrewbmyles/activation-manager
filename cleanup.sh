#!/bin/bash

# Activation Manager Cleanup Script
# Archives redundant files and cleans up the codebase

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create archive directory with timestamp
ARCHIVE_DIR="archive/cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo -e "${YELLOW}🧹 Starting cleanup of redundant files...${NC}"

# Archive redundant backend files
echo -e "${YELLOW}Archiving redundant backend files...${NC}"
BACKEND_FILES=(
    "demo_backend.py"
    "fixed_backend.py"
    "simple_working_backend.py"
    "debug_backend.py"
    "production_backend.py"
    "no_auth_backend.py"
    "test_backend.py"
    "unified_api.py"
    "final_demo.py"
    "demo_enhanced_system.py"
    "simple_variable_selector_demo.py"
    "audience_webserver_extension.py"
    "workflow_nlweb_handler.py"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo -e "${GREEN}✓ Archived: $file${NC}"
    fi
done

# Archive redundant startup scripts
echo -e "${YELLOW}Archiving redundant startup scripts...${NC}"
STARTUP_SCRIPTS=(
    "start_demo.py"
    "start_demo.sh"
    "start_enhanced_demo.sh"
    "start_frontend.sh"
    "start_integrated_demo.sh"
    "start_no_auth.sh"
    "start_production_demo.sh"
    "start_simple.sh"
    "start_with_variable_picker.sh"
    "start_working.sh"
    "start_working_demo.sh"
    "start_backend_only.sh"
    "debug_launch.sh"
    "check_backend.sh"
    "DEMO_START.sh"
)

for file in "${STARTUP_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo -e "${GREEN}✓ Archived: $file${NC}"
    fi
done

# Archive old enhanced variable selector versions
echo -e "${YELLOW}Archiving old variable selector versions...${NC}"
OLD_VERSIONS=(
    "activation_manager/core/enhanced_variable_selector_v2.py"
    "activation_manager/core/enhanced_variable_selector_v3.py"
    "activation_manager/core/enhanced_variable_selector_v4.py"
    "activation_manager/core/enhanced_variable_selector_v5.py"
)

for file in "${OLD_VERSIONS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo -e "${GREEN}✓ Archived: $file${NC}"
    fi
done

# Archive test and utility scripts
echo -e "${YELLOW}Archiving redundant test scripts...${NC}"
TEST_SCRIPTS=(
    "test_*.py"
    "diagnose_*.py"
    "analyze_*.py"
    "generate_*.py"
    "fix_*.py"
    "troubleshoot.py"
    "update_embeddings_config.py"
    "setup_embeddings.py"
    "performance_test_embeddings.py"
)

for pattern in "${TEST_SCRIPTS[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ] && [ "$file" != "test_app.py" ]; then
            mv "$file" "$ARCHIVE_DIR/"
            echo -e "${GREEN}✓ Archived: $file${NC}"
        fi
    done
done

# Archive deployment scripts we don't need
echo -e "${YELLOW}Archiving unused deployment scripts...${NC}"
DEPLOY_SCRIPTS=(
    "deploy-to-vercel.sh"
)

for file in "${DEPLOY_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo -e "${GREEN}✓ Archived: $file${NC}"
    fi
done

# Clean up duplicate data directories
echo -e "${YELLOW}Consolidating data directories...${NC}"
if [ -d "data/embeddings" ] && [ -d "activation_manager/data/embeddings" ]; then
    # Check which one has more files
    DATA_COUNT=$(find data/embeddings -type f | wc -l)
    AM_DATA_COUNT=$(find activation_manager/data/embeddings -type f | wc -l)
    
    if [ $DATA_COUNT -gt $AM_DATA_COUNT ]; then
        echo -e "${YELLOW}Moving embeddings to activation_manager/data/embeddings...${NC}"
        cp -r data/embeddings/* activation_manager/data/embeddings/ 2>/dev/null
        rm -rf data/embeddings
        echo -e "${GREEN}✓ Consolidated embeddings data${NC}"
    fi
fi

# Archive old documentation
echo -e "${YELLOW}Archiving old documentation...${NC}"
OLD_DOCS=(
    "BUG_FIXES_LOG.md"
    "BUG_FIXES_SUMMARY.md"
    "DEMO_GUIDE.md"
    "DEMO_READY.md"
    "DEMO_READY_STATUS.md"
    "DEPLOYMENT_CHECKLIST.md"
    "ENHANCED_TESTING_SUMMARY.md"
    "ENHANCEMENT_SUMMARY.md"
    "GIT_COMMIT_SUMMARY.md"
    "IMPROVEMENT_ACTION_PLAN.md"
    "LAUNCH_INSTRUCTIONS.md"
    "NL_INTERFACE_FIX.md"
    "VARIABLE_PICKER_IMPLEMENTATION.md"
    "workflow_diagrams.md"
    "test_results_summary.md"
)

for file in "${OLD_DOCS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo -e "${GREEN}✓ Archived: $file${NC}"
    fi
done

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo -e "${YELLOW}Creating .env.example...${NC}"
    cat > .env.example << EOF
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Environment
FLASK_ENV=development
PORT=8080

# Features
USE_EMBEDDINGS=true
USE_NLWEB=false

# Database
DATABASE_URL=sqlite:///activation_manager.db

# Google Cloud (for deployment)
GCP_PROJECT_ID=your_project_id
GCP_REGION=us-central1
EOF
    echo -e "${GREEN}✓ Created .env.example${NC}"
fi

# Summary
echo -e "\n${GREEN}✅ Cleanup complete!${NC}"
echo -e "${YELLOW}Files archived to: $ARCHIVE_DIR${NC}"
echo -e "${YELLOW}Total files archived: $(find $ARCHIVE_DIR -type f | wc -l)${NC}"

echo -e "\n${GREEN}Refactored structure:${NC}"
echo "- Single backend: backend.py"
echo "- Single startup script: start.sh"
echo "- Consolidated variable selector: activation_manager/core/variable_selector.py"
echo "- Clean configuration: activation_manager/config/settings.py"
echo "- Deployment ready: app.yaml, Dockerfile"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Review archived files in $ARCHIVE_DIR"
echo "2. Delete archive directory if everything looks good"
echo "3. Test the application with: ./start.sh --mode local"
echo "4. Deploy to GCP with: gcloud app deploy"