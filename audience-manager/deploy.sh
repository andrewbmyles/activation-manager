#!/bin/bash

# Deployment script for Audience Manager
# Supports multiple deployment targets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DEPLOY_TARGET="docker"
ENVIRONMENT="production"
SKIP_BUILD=false
SKIP_TESTS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            DEPLOY_TARGET="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --target      Deployment target (docker, vercel, aws, heroku, railway)"
            echo "  --env         Environment (development, staging, production)"
            echo "  --skip-build  Skip building the application"
            echo "  --skip-tests  Skip running tests"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}Audience Manager Deployment Script${NC}"
echo -e "Target: ${YELLOW}$DEPLOY_TARGET${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo ""

# Run tests unless skipped
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${YELLOW}Running tests...${NC}"
    npm test -- --watchAll=false
    cd src/api && python -m pytest
    cd ../..
fi

# Build application unless skipped
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}Building application...${NC}"
    npm run build
fi

# Deploy based on target
case $DEPLOY_TARGET in
    docker)
        echo -e "${YELLOW}Deploying with Docker Compose...${NC}"
        
        # Check if .env exists
        if [ ! -f .env ]; then
            echo -e "${YELLOW}Creating .env from .env.example...${NC}"
            cp .env.example .env
            echo -e "${RED}Please update .env with your configuration${NC}"
            exit 1
        fi
        
        # Build and start containers
        docker-compose build
        docker-compose up -d
        
        echo -e "${GREEN}Deployment complete!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:5000"
        echo "To view logs: docker-compose logs -f"
        ;;
        
    vercel)
        echo -e "${YELLOW}Deploying to Vercel...${NC}"
        
        # Check if vercel CLI is installed
        if ! command -v vercel &> /dev/null; then
            echo -e "${RED}Vercel CLI not found. Installing...${NC}"
            npm i -g vercel
        fi
        
        # Deploy based on environment
        if [ "$ENVIRONMENT" = "production" ]; then
            vercel --prod
        else
            vercel
        fi
        ;;
        
    aws)
        echo -e "${YELLOW}Deploying to AWS...${NC}"
        
        # Check AWS CLI
        if ! command -v aws &> /dev/null; then
            echo -e "${RED}AWS CLI not found. Please install it first.${NC}"
            exit 1
        fi
        
        # Build Docker images
        docker build -f Dockerfile.frontend -t audience-manager-frontend .
        docker build -f Dockerfile.backend -t audience-manager-backend .
        
        # Tag and push to ECR (assumes ECR repositories exist)
        AWS_REGION=${AWS_REGION:-us-east-1}
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
        
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
        
        docker tag audience-manager-frontend:latest $ECR_REGISTRY/audience-manager-frontend:latest
        docker tag audience-manager-backend:latest $ECR_REGISTRY/audience-manager-backend:latest
        
        docker push $ECR_REGISTRY/audience-manager-frontend:latest
        docker push $ECR_REGISTRY/audience-manager-backend:latest
        
        echo -e "${GREEN}Images pushed to ECR!${NC}"
        echo "Update your ECS task definitions with the new images"
        ;;
        
    heroku)
        echo -e "${YELLOW}Deploying to Heroku...${NC}"
        
        # Check Heroku CLI
        if ! command -v heroku &> /dev/null; then
            echo -e "${RED}Heroku CLI not found. Please install it first.${NC}"
            exit 1
        fi
        
        # Create Heroku apps if they don't exist
        heroku create audience-manager-frontend --region us || true
        heroku create audience-manager-backend --region us || true
        
        # Deploy frontend
        git subtree push --prefix=. heroku-frontend main
        
        # Deploy backend
        cd src/api
        git init
        git add .
        git commit -m "Deploy backend"
        heroku git:remote -a audience-manager-backend
        git push heroku main -f
        cd ../..
        
        echo -e "${GREEN}Deployment to Heroku complete!${NC}"
        ;;
        
    railway)
        echo -e "${YELLOW}Deploying to Railway...${NC}"
        
        # Check Railway CLI
        if ! command -v railway &> /dev/null; then
            echo -e "${RED}Railway CLI not found. Installing...${NC}"
            npm i -g @railway/cli
        fi
        
        # Deploy
        railway up
        
        echo -e "${GREEN}Deployment to Railway complete!${NC}"
        ;;
        
    *)
        echo -e "${RED}Unknown deployment target: $DEPLOY_TARGET${NC}"
        echo "Valid targets: docker, vercel, aws, heroku, railway"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"