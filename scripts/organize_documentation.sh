#!/bin/bash
# Organize documentation files

echo "Organizing documentation files..."
echo "================================"

# Create documentation directories
mkdir -p docs/{archive,deployment,features,testing,development}

# Define documentation categories and patterns
declare -A DOC_CATEGORIES=(
    ["deployment"]="DEPLOY|DEPLOYMENT|GCP|STAGING|PRODUCTION|TOBERMORY"
    ["features"]="FEATURE|ENHANCEMENT|AUDIENCE|VARIABLE|PICKER|SEMANTIC|PERSISTENCE"
    ["testing"]="TEST|TESTING|BUG|FIX|HOTFIX"
    ["development"]="REFACTOR|PLAN|GUIDE|TECHNICAL|ARCHITECTURE"
)

# Keep these in root
KEEP_IN_ROOT=(
    "README.md"
    "README_NEW.md"
    "CHANGELOG.md"
    "LICENSE"
    "DEPLOYMENT_QUICK_GUIDE.md"
    "REFACTORING_IMPLEMENTATION_SUMMARY.md"
)

echo "Organizing documentation by category..."

# Function to check if file should be kept in root
should_keep_in_root() {
    local file=$1
    for keep_file in "${KEEP_IN_ROOT[@]}"; do
        if [[ "$file" == "$keep_file" ]]; then
            return 0
        fi
    done
    return 1
}

# Move files by category
for category in "${!DOC_CATEGORIES[@]}"; do
    pattern="${DOC_CATEGORIES[$category]}"
    echo -e "\n$category documents:"
    
    for file in *.md; do
        if should_keep_in_root "$file"; then
            continue
        fi
        
        if [[ "$file" =~ $pattern ]]; then
            mv "$file" "docs/$category/"
            echo "  → Moved $file"
        fi
    done
done

# Move remaining .md files to archive
echo -e "\nArchiving other documentation:"
for file in *.md; do
    if should_keep_in_root "$file"; then
        echo "  ✓ Keeping $file in root"
    else
        mv "$file" "docs/archive/"
        echo "  → Archived $file"
    fi
done

echo -e "\n✅ Documentation organized!"
echo "Categories created:"
echo "  - docs/deployment/ - Deployment guides"
echo "  - docs/features/ - Feature documentation"
echo "  - docs/testing/ - Test reports and fixes"
echo "  - docs/development/ - Development guides"
echo "  - docs/archive/ - Other documentation"