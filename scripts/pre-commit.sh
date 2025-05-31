#!/bin/bash
# Pre-commit hook to remind about staging deployment

# Colors
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}📋 Pre-commit Reminder${NC}"
echo -e "${BLUE}═══════════════════════${NC}"
echo ""
echo "After committing, remember to:"
echo "1. Deploy to staging: ./deploy.sh -e staging"
echo "2. Test your changes"
echo "3. Promote to production: ./promote-to-prod.sh stg-VERSION"
echo ""
echo -e "${YELLOW}Tip:${NC} Never deploy directly to production!"
echo ""

# Run any linting or tests here
# exit 1 to prevent commit if tests fail

exit 0