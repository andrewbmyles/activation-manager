#!/bin/bash

# Activation Manager Unified Startup Script
# Supports both local development and GCP deployment

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
MODE="local"
PORT="8080"
FRONTEND_PORT="3000"
ENV="development"
USE_FULL_BACKEND=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --full)
            USE_FULL_BACKEND=true
            shift
            ;;
        --help)
            echo "Usage: ./start.sh [options]"
            echo "Options:"
            echo "  --mode [local|production|docker]  Deployment mode (default: local)"
            echo "  --port PORT                       Backend port (default: 8080)"
            echo "  --env [development|production]    Environment (default: development)"
            echo "  --full                           Use full backend with embeddings"
            echo "  --help                           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🚀 Starting Activation Manager${NC}"
echo -e "${BLUE}Mode: $MODE, Environment: $ENV, Port: $PORT${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    local port=$1
    if port_in_use $port; then
        echo -e "${YELLOW}Port $port is in use. Killing existing process...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 2  # Give more time for port to be released
        
        # Double check and force kill if still in use
        if port_in_use $port; then
            echo -e "${YELLOW}Port $port still in use. Force killing...${NC}"
            sudo lsof -ti:$port | xargs sudo kill -9 2>/dev/null || true
            sleep 1
        fi
    fi
}

# Set environment variables
export FLASK_ENV=$ENV
export PORT=$PORT

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo -e "${GREEN}✓ Loading environment variables from .env${NC}"
    set -a
    source .env
    set +a
fi

case $MODE in
    "local")
        echo -e "${BLUE}Starting in local development mode...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}Creating virtual environment...${NC}"
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        echo -e "${GREEN}✓ Activating virtual environment${NC}"
        source venv/bin/activate
        
        # Install dependencies
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements.txt --quiet
        
        # Kill existing processes
        kill_port $PORT
        kill_port $FRONTEND_PORT
        
        # Start backend
        echo -e "${GREEN}✓ Starting backend on port $PORT${NC}"
        # Use simple backend for quick start, switch to full backend with --full flag
        if [[ "$USE_FULL_BACKEND" == "true" ]]; then
            echo -e "${YELLOW}Loading full dataset with embeddings (this may take 30-60 seconds)...${NC}"
            python backend.py &
        else
            echo -e "${BLUE}Using simple backend with mock data for quick start${NC}"
            python backend_simple.py &
        fi
        BACKEND_PID=$!
        
        # Check if frontend exists and should be started
        if [ -d "audience-manager" ] && command_exists npm; then
            echo -e "${GREEN}✓ Starting frontend on port $FRONTEND_PORT${NC}"
            cd audience-manager
            npm install --silent
            npm start &
            FRONTEND_PID=$!
            cd ..
        fi
        
        # Wait for services to start
        echo -e "${YELLOW}Waiting for services to start...${NC}"
        sleep 5
        
        # Check if backend is actually running
        if ! curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            echo -e "${RED}❌ Backend failed to start properly${NC}"
            echo -e "${YELLOW}Checking backend logs...${NC}"
            # Try to restart backend
            kill $BACKEND_PID 2>/dev/null || true
            sleep 1
            if [[ "$USE_FULL_BACKEND" == "true" ]]; then
                python backend.py &
            else
                python backend_simple.py &
            fi
            BACKEND_PID=$!
            sleep 3
        fi
        
        # Display access information
        echo -e "\n${GREEN}✅ Activation Manager is running!${NC}"
        echo -e "${BLUE}Backend: http://localhost:$PORT${NC}"
        echo -e "${BLUE}API Health: http://localhost:$PORT/health${NC}"
        if [ ! -z "$FRONTEND_PID" ]; then
            echo -e "${BLUE}Frontend: http://localhost:$FRONTEND_PORT${NC}"
        fi
        echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"
        
        # Function to cleanup on exit
        cleanup() {
            echo -e "\n${YELLOW}Shutting down services...${NC}"
            kill $BACKEND_PID 2>/dev/null
            [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
            kill_port $PORT
            kill_port $FRONTEND_PORT
            echo -e "${GREEN}✓ All services stopped${NC}"
            exit 0
        }
        
        # Set trap for cleanup
        trap cleanup INT TERM
        
        # Wait for background processes
        wait
        ;;
        
    "production")
        echo -e "${BLUE}Starting in production mode...${NC}"
        
        # Check if gunicorn is installed
        if ! command_exists gunicorn; then
            echo -e "${YELLOW}Installing gunicorn...${NC}"
            pip install gunicorn
        fi
        
        # Start with gunicorn
        echo -e "${GREEN}✓ Starting production server with gunicorn${NC}"
        gunicorn -b 0.0.0.0:$PORT \
                 -w 4 \
                 --timeout 120 \
                 --log-level info \
                 --access-logfile - \
                 --error-logfile - \
                 backend:app
        ;;
        
    "docker")
        echo -e "${BLUE}Starting with Docker...${NC}"
        
        # Check if Docker is installed
        if ! command_exists docker; then
            echo -e "${RED}❌ Docker is not installed${NC}"
            exit 1
        fi
        
        # Check if docker-compose exists
        if [ -f "docker-compose.yml" ]; then
            echo -e "${GREEN}✓ Starting with docker-compose${NC}"
            docker-compose up --build
        else
            echo -e "${YELLOW}Building Docker image...${NC}"
            docker build -t activation-manager .
            
            echo -e "${GREEN}✓ Running Docker container${NC}"
            docker run -p $PORT:$PORT \
                      -e PORT=$PORT \
                      -e FLASK_ENV=$ENV \
                      --name activation-manager \
                      activation-manager
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Unknown mode: $MODE${NC}"
        exit 1
        ;;
esac