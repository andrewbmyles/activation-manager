#!/bin/bash
# Organize deployment scripts

echo "Organizing deployment scripts..."
echo "================================"

# Create directories
mkdir -p scripts/deploy scripts/archive

# Keep these essential scripts in scripts/deploy
KEEP_SCRIPTS=(
    "deploy-staging.sh"
    "promote-to-prod.sh"
    "deploy-local.sh"
    "deploy-cost-optimized.sh"
)

# Copy essential scripts
echo "Keeping essential scripts:"
for script in "${KEEP_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        cp "$script" scripts/deploy/
        echo "  ✓ $script"
    fi
done

# Archive all other deploy scripts
echo -e "\nArchiving other deployment scripts:"
for script in deploy-*.sh; do
    if [[ ! " ${KEEP_SCRIPTS[@]} " =~ " ${script} " ]]; then
        mv "$script" scripts/archive/
        echo "  → Archived $script"
    fi
done

# Move the essential scripts to scripts/deploy
echo -e "\nMoving essential scripts to scripts/deploy:"
for script in "${KEEP_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" scripts/deploy/
        echo "  ✓ Moved $script"
    fi
done

echo -e "\n✅ Deployment scripts organized!"
echo "Essential scripts in: scripts/deploy/"
echo "Archived scripts in: scripts/archive/"