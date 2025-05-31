#!/bin/bash
# Activation Manager - Master Deployment Script
# This script consolidates all deployment functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-feisty-catcher-461000-g2}"
DEFAULT_VERSION_PREFIX="v"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Functions
print_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -e, --env ENV        Environment (dev|staging|prod) [default: prod]"
    echo "  -v, --version VER    Version name [default: auto-generated]"
    echo "  -p, --project ID     GCP Project ID [default: $PROJECT_ID]"
    echo "  --no-promote         Don't promote to live traffic"
    echo "  --skip-build         Skip frontend build"
    echo "  --skip-tests         Skip running tests"
    echo ""
    echo "Examples:"
    echo "  $0                           # Deploy to production"
    echo "  $0 -e staging                # Deploy to staging"
    echo "  $0 -v hotfix-1 --no-promote  # Deploy hotfix without promoting"
}

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}     Activation Manager Deployment Script${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ Node.js is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js $(node --version)${NC}"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}✗ npm is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ npm $(npm --version)${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python $(python3 --version)${NC}"
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}✗ Google Cloud SDK is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Google Cloud SDK$(NC}"
    
    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        echo -e "${RED}✗ Not authenticated with Google Cloud${NC}"
        echo "Run: gcloud auth login"
        exit 1
    fi
    echo -e "${GREEN}✓ Authenticated as $(gcloud auth list --filter=status:ACTIVE --format='value(account)')${NC}"
    
    echo ""
}

check_data_files() {
    echo -e "${YELLOW}Checking data files...${NC}"
    
    if [ -f "data/Full_Variable_List_2022_CAN.csv" ]; then
        echo -e "${GREEN}✓ CSV data file found${NC}"
    else
        echo -e "${RED}✗ CSV data file missing!${NC}"
        exit 1
    fi
    
    if [ -f "data/variables_2022_can.parquet" ]; then
        echo -e "${GREEN}✓ Parquet data file found${NC}"
    else
        echo -e "${YELLOW}⚠ Parquet file missing (will use CSV)${NC}"
    fi
    
    echo ""
}

run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        echo -e "${YELLOW}Skipping tests...${NC}"
        return
    fi
    
    echo -e "${YELLOW}Running tests...${NC}"
    
    # Frontend tests
    echo -e "${BLUE}Running frontend tests...${NC}"
    cd audience-manager
    npm test -- --watchAll=false --passWithNoTests || {
        echo -e "${RED}✗ Frontend tests failed${NC}"
        exit 1
    }
    cd ..
    echo -e "${GREEN}✓ Frontend tests passed${NC}"
    
    # Backend tests
    echo -e "${BLUE}Running backend tests...${NC}"
    python3 -m pytest --tb=short -q 2>/dev/null || {
        echo -e "${YELLOW}⚠ Backend tests not found or failed${NC}"
    }
    
    echo ""
}

build_frontend() {
    if [ "$SKIP_BUILD" = true ]; then
        echo -e "${YELLOW}Skipping frontend build...${NC}"
        return
    fi
    
    echo -e "${YELLOW}Building frontend...${NC}"
    cd audience-manager
    
    # Clean previous build
    rm -rf build
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}Installing dependencies...${NC}"
        npm install
    fi
    
    # Build
    npm run build || {
        echo -e "${RED}✗ Frontend build failed${NC}"
        exit 1
    }
    
    # Verify build
    if [ ! -d "build" ]; then
        echo -e "${RED}✗ Build directory not created${NC}"
        exit 1
    fi
    
    cd ..
    echo -e "${GREEN}✓ Frontend built successfully${NC}"
    echo ""
}

select_app_yaml() {
    case $ENVIRONMENT in
        dev)
            APP_YAML="app_development.yaml"
            ;;
        staging)
            # Use production config for staging
            APP_YAML="app_production.yaml"
            # Force no-promote for staging
            NO_PROMOTE=true
            ;;
        prod|production)
            APP_YAML="app_production.yaml"
            ;;
        *)
            echo -e "${RED}✗ Unknown environment: $ENVIRONMENT${NC}"
            exit 1
            ;;
    esac
    
    if [ ! -f "$APP_YAML" ]; then
        echo -e "${YELLOW}⚠ $APP_YAML not found, using app_production.yaml${NC}"
        APP_YAML="app_production.yaml"
    fi
}

deploy() {
    echo -e "${YELLOW}Deploying to Google App Engine...${NC}"
    echo -e "${BLUE}Project: $PROJECT_ID${NC}"
    echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
    echo -e "${BLUE}Version: $VERSION_NAME${NC}"
    echo -e "${BLUE}Config: $APP_YAML${NC}"
    echo ""
    
    # Build deployment command
    DEPLOY_CMD="gcloud app deploy $APP_YAML"
    DEPLOY_CMD="$DEPLOY_CMD --project=$PROJECT_ID"
    DEPLOY_CMD="$DEPLOY_CMD --version=$VERSION_NAME"
    
    if [ "$NO_PROMOTE" = true ]; then
        DEPLOY_CMD="$DEPLOY_CMD --no-promote"
    else
        DEPLOY_CMD="$DEPLOY_CMD --promote"
    fi
    
    DEPLOY_CMD="$DEPLOY_CMD --quiet"
    
    # Execute deployment
    $DEPLOY_CMD || {
        echo -e "${RED}✗ Deployment failed${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
}

show_post_deployment_info() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo -e "${YELLOW}Version: $VERSION_NAME${NC}"
    echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
    
    if [ "$NO_PROMOTE" = true ]; then
        echo -e "${YELLOW}Status: Deployed (not promoted)${NC}"
        echo ""
        if [ "$ENVIRONMENT" = "staging" ]; then
            echo -e "${YELLOW}Staging URL:${NC}"
            echo -e "${BLUE}https://$VERSION_NAME-dot-$PROJECT_ID.appspot.com${NC}"
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "1. Test using STAGING_TEST_CHECKLIST.md"
            echo "2. Monitor logs: gcloud app logs tail --version=$VERSION_NAME"
            echo "3. When ready, promote to production:"
            echo -e "${BLUE}./promote-to-prod.sh $VERSION_NAME${NC}"
        else
            echo "To promote this version:"
            echo -e "${BLUE}gcloud app versions migrate $VERSION_NAME --project=$PROJECT_ID${NC}"
        fi
    else
        echo -e "${YELLOW}Status: Live${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}URLs:${NC}"
    if [ "$ENVIRONMENT" = "prod" ] || [ "$ENVIRONMENT" = "production" ]; then
        echo "Production: https://tobermory.ai"
    elif [ "$ENVIRONMENT" = "staging" ]; then
        echo "Staging: https://$VERSION_NAME-dot-$PROJECT_ID.appspot.com"
    fi
    echo "App Engine: https://$PROJECT_ID.appspot.com"
    
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    if [ "$ENVIRONMENT" = "staging" ]; then
        echo "View logs:      gcloud app logs tail --version=$VERSION_NAME"
    else
        echo "View logs:      gcloud app logs tail -s default"
    fi
    echo "List versions:  gcloud app versions list"
    echo "View instances: gcloud app instances list"
    
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
}

# Parse arguments
ENVIRONMENT="prod"
VERSION_NAME=""
NO_PROMOTE=false
SKIP_BUILD=false
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION_NAME="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --no-promote)
            NO_PROMOTE=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Auto-generate version name if not provided
if [ -z "$VERSION_NAME" ]; then
    case $ENVIRONMENT in
        dev)
            VERSION_NAME="dev-${TIMESTAMP}"
            ;;
        staging)
            VERSION_NAME="staging-${TIMESTAMP}"
            ;;
        prod|production)
            VERSION_NAME="${DEFAULT_VERSION_PREFIX}${TIMESTAMP}"
            ;;
    esac
fi

# Main execution
print_header
check_prerequisites
check_data_files
select_app_yaml
run_tests
build_frontend
deploy
show_post_deployment_info