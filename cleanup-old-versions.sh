#!/bin/bash
# Clean up old App Engine versions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-feisty-catcher-461000-g2}"
KEEP_STAGING=5
KEEP_PRODUCTION=10
KEEP_DAYS=7

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        App Engine Version Cleanup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "Policy:"
echo -e "  - Keep last ${KEEP_STAGING} staging versions"
echo -e "  - Keep last ${KEEP_PRODUCTION} production versions"
echo -e "  - Keep all versions < ${KEEP_DAYS} days old"
echo -e "  - Never delete currently serving versions"
echo ""

# Get current serving version
echo -e "${YELLOW}Current serving version:${NC}"
SERVING=$(gcloud app versions list --filter="traffic_split>0" --format="value(version.id)" --project="${PROJECT_ID}")
echo -e "${GREEN}${SERVING}${NC}"
echo ""

# Find old staging versions
echo -e "${YELLOW}Finding old staging versions...${NC}"
OLD_STAGING=$(gcloud app versions list \
  --filter="version.id:stg-* AND traffic_split=0" \
  --sort-by="~version.createTime" \
  --format="value(version.id)" \
  --project="${PROJECT_ID}" | tail -n +$((KEEP_STAGING + 1)))

# Find old production versions (non-staging)
echo -e "${YELLOW}Finding old production versions...${NC}"
OLD_PROD=$(gcloud app versions list \
  --filter="NOT version.id:stg-* AND traffic_split=0" \
  --sort-by="~version.createTime" \
  --format="value(version.id)" \
  --project="${PROJECT_ID}" | tail -n +$((KEEP_PRODUCTION + 1)))

# Combine and filter by age
ALL_OLD="$OLD_STAGING $OLD_PROD"
VERSIONS_TO_DELETE=""

for version in $ALL_OLD; do
  # Skip if empty
  if [ -z "$version" ]; then
    continue
  fi
  
  # Get version age
  CREATE_TIME=$(gcloud app versions describe "$version" \
    --service=default \
    --format="value(createTime)" \
    --project="${PROJECT_ID}" 2>/dev/null || echo "")
  
  if [ -n "$CREATE_TIME" ]; then
    # Convert to seconds since epoch
    CREATE_EPOCH=$(date -d "$CREATE_TIME" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$CREATE_TIME" +%s 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    AGE_DAYS=$(( (NOW_EPOCH - CREATE_EPOCH) / 86400 ))
    
    if [ $AGE_DAYS -gt $KEEP_DAYS ]; then
      VERSIONS_TO_DELETE="$VERSIONS_TO_DELETE $version"
    fi
  fi
done

# Remove leading/trailing spaces and check if empty
VERSIONS_TO_DELETE=$(echo "$VERSIONS_TO_DELETE" | xargs)

if [ -z "$VERSIONS_TO_DELETE" ]; then
  echo -e "${GREEN}No old versions to delete!${NC}"
  echo "All versions are either:"
  echo "  - Currently serving"
  echo "  - Within retention policy"
  echo "  - Less than ${KEEP_DAYS} days old"
  exit 0
fi

# Show versions to delete
echo -e "\n${YELLOW}Versions to delete:${NC}"
for version in $VERSIONS_TO_DELETE; do
  echo "  - $version"
done

# Count versions
VERSION_COUNT=$(echo "$VERSIONS_TO_DELETE" | wc -w)
echo -e "\n${YELLOW}Total versions to delete: ${VERSION_COUNT}${NC}"

# Confirm deletion
echo ""
read -p "Do you want to delete these versions? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "\n${YELLOW}Deleting old versions...${NC}"
  
  # Delete versions one by one to show progress
  DELETED=0
  FAILED=0
  
  for version in $VERSIONS_TO_DELETE; do
    echo -n "Deleting $version... "
    if gcloud app versions delete "$version" \
      --service=default \
      --quiet \
      --project="${PROJECT_ID}" 2>/dev/null; then
      echo -e "${GREEN}✓${NC}"
      ((DELETED++))
    else
      echo -e "${RED}✗${NC}"
      ((FAILED++))
    fi
  done
  
  echo ""
  echo -e "${BLUE}================================================${NC}"
  echo -e "${GREEN}Cleanup Complete!${NC}"
  echo -e "${BLUE}================================================${NC}"
  echo -e "Deleted: ${GREEN}${DELETED}${NC} versions"
  if [ $FAILED -gt 0 ]; then
    echo -e "Failed: ${RED}${FAILED}${NC} versions"
  fi
  
  # Show remaining versions
  echo ""
  echo -e "${YELLOW}Remaining versions:${NC}"
  gcloud app versions list --format="table(version.id,traffic_split,createTime.date())" --project="${PROJECT_ID}"
else
  echo -e "${YELLOW}Cleanup cancelled${NC}"
fi