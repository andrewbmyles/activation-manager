#!/bin/bash

# Deployment Monitoring Script for Audience Manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Audience Manager Deployment Status ===${NC}"
echo ""

# Check domain mapping status
echo -e "${YELLOW}Checking domain mapping status...${NC}"
echo ""

echo -e "${BLUE}Frontend (tobermory.ai):${NC}"
FRONTEND_STATUS=$(gcloud beta run domain-mappings describe --domain tobermory.ai --region us-central1 --format="value(status.conditions[0].message)" 2>/dev/null || echo "Not found")
if [[ "$FRONTEND_STATUS" == *"serving"* ]]; then
    echo -e "${GREEN}✓ SSL certificate active - domain is ready!${NC}"
    echo "  Access at: https://tobermory.ai"
else
    echo -e "${YELLOW}⏳ SSL certificate pending: $FRONTEND_STATUS${NC}"
    echo "  Temporary URL: https://audience-manager-593977832320.us-central1.run.app"
fi

echo ""
echo -e "${BLUE}API (api.tobermory.ai):${NC}"
API_STATUS=$(gcloud beta run domain-mappings describe --domain api.tobermory.ai --region us-central1 --format="value(status.conditions[0].message)" 2>/dev/null || echo "Not found")
if [[ "$API_STATUS" == *"serving"* ]]; then
    echo -e "${GREEN}✓ SSL certificate active - domain is ready!${NC}"
    echo "  Access at: https://api.tobermory.ai"
else
    echo -e "${YELLOW}⏳ SSL certificate pending: $API_STATUS${NC}"
    echo "  Temporary URL: https://audience-manager-api-593977832320.us-central1.run.app"
fi

echo ""
echo -e "${BLUE}Service Health:${NC}"

# Test with authentication token
TOKEN=$(gcloud auth print-identity-token 2>/dev/null || echo "")
if [ ! -z "$TOKEN" ]; then
    HEALTH_CHECK=$(curl -s -H "Authorization: Bearer $TOKEN" https://audience-manager-api-593977832320.us-central1.run.app/health | grep -o '"status":"healthy"' || echo "failed")
    if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
        echo -e "${GREEN}✓ API is healthy${NC}"
    else
        echo -e "${RED}✗ API health check failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Cannot check API health (authentication required)${NC}"
fi

echo ""
echo -e "${BLUE}Quick Actions:${NC}"
echo "1. Test frontend: open https://audience-manager-593977832320.us-central1.run.app"
echo "2. Login with: andrew@tobermory.ai / admin"
echo "3. Check logs: gcloud logs read --service=audience-manager --limit=10"
echo ""
echo -e "${YELLOW}SSL certificates typically provision within 15 minutes to 24 hours.${NC}"
echo -e "${YELLOW}Run this script again to check status: ./monitor-deployment.sh${NC}"