#!/bin/bash
# Promote staging version to production

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-feisty-catcher-461000-g2}"

# Check if version provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide staging version to promote${NC}"
    echo "Usage: $0 <staging-version>"
    echo ""
    echo -e "${YELLOW}Available staging versions:${NC}"
    gcloud app versions list --filter="version.id:stg-*" --format="table(version.id,traffic_split,last_deployed_time.date())" --project="${PROJECT_ID}"
    exit 1
fi

STAGING_VERSION=$1

# Verify it's a staging version
if [[ ! "$STAGING_VERSION" =~ ^stg- ]]; then
    echo -e "${RED}Error: Version must be a staging version (stg-*)${NC}"
    exit 1
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        Promote Staging to Production${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Version: ${YELLOW}${STAGING_VERSION}${NC}"
echo -e "Project: ${YELLOW}${PROJECT_ID}${NC}"
echo ""

# Check if version exists
if ! gcloud app versions describe "${STAGING_VERSION}" --service=default --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${RED}Error: Version ${STAGING_VERSION} not found${NC}"
    exit 1
fi

# Show current traffic split
echo -e "${YELLOW}Current production version:${NC}"
CURRENT_PROD=$(gcloud app versions list --filter="traffic_split>0" --format="value(version.id)" --project="${PROJECT_ID}" --limit=1)
echo -e "${BLUE}${CURRENT_PROD}${NC}"
echo ""

# Show staging version details
echo -e "${YELLOW}Staging version details:${NC}"
gcloud app versions describe "${STAGING_VERSION}" --service=default --project="${PROJECT_ID}" --format="table(
    id,
    createTime.date(),
    servingStatus
)"
echo ""

# Confirmation with checklist
echo -e "${YELLOW}Pre-promotion checklist:${NC}"
echo "Have you verified the following in staging?"
echo ""
echo "  [ ] Login functionality works"
echo "  [ ] Variable search returns results"
echo "  [ ] Refine feature works properly"
echo "  [ ] Export functionality works"
echo "  [ ] No errors in logs"
echo "  [ ] Performance is acceptable"
echo ""

read -p "Have you completed all checks? (yes/no) " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Promotion cancelled - please complete staging tests first${NC}"
    exit 0
fi

echo ""
read -p "Are you sure you want to promote ${STAGING_VERSION} to production? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Promoting staging to production...${NC}"
    
    # Promote staging to production
    gcloud app versions migrate "${STAGING_VERSION}" \
      --service=default \
      --quiet \
      --project="${PROJECT_ID}"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Successfully promoted ${STAGING_VERSION} to production!${NC}"
        
        # Show new traffic allocation
        echo ""
        echo -e "${YELLOW}New traffic allocation:${NC}"
        gcloud app versions list --filter="traffic_split>0" --format="table(version.id,traffic_split,servingStatus)" --project="${PROJECT_ID}"
        
        # Create production tag for reference
        PROD_VERSION="prod-${STAGING_VERSION#stg-}"
        echo ""
        echo -e "${YELLOW}Production reference: ${PROD_VERSION}${NC}"
        
        # Show rollback command
        echo ""
        echo -e "${BLUE}================================================${NC}"
        echo -e "${GREEN}Promotion Complete!${NC}"
        echo -e "${BLUE}================================================${NC}"
        echo ""
        echo -e "${YELLOW}Production URL:${NC} https://tobermory.ai"
        echo ""
        echo -e "${YELLOW}To rollback if needed:${NC}"
        echo -e "${BLUE}gcloud app versions migrate ${CURRENT_PROD} --project=${PROJECT_ID}${NC}"
        echo ""
        echo -e "${YELLOW}To view logs:${NC}"
        echo -e "${BLUE}gcloud app logs tail -s default --project=${PROJECT_ID}${NC}"
        echo ""
        
        # Suggest cleanup
        echo -e "${YELLOW}Consider cleaning up old versions:${NC}"
        OLD_VERSIONS=$(gcloud app versions list --filter="traffic_split=0 AND version.id:stg-*" --format="value(version.id)" --limit=5 --project="${PROJECT_ID}")
        if [ -n "$OLD_VERSIONS" ]; then
            echo "$OLD_VERSIONS"
            echo ""
            echo "To delete old staging versions:"
            echo -e "${BLUE}gcloud app versions delete $OLD_VERSIONS --project=${PROJECT_ID}${NC}"
        else
            echo "No old staging versions to clean up"
        fi
    else
        echo -e "${RED}✗ Promotion failed!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Promotion cancelled${NC}"
fi