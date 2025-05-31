#!/bin/bash

echo "🧹 Cleaning up project directory..."
echo "==================================="

# Remove test scripts
echo "Removing test scripts..."
rm -f test-*.sh
rm -f test-*.py

# Remove temporary deployment scripts
echo "Removing temporary deployment scripts..."
rm -f deploy-hotfix.sh
rm -f deploy-enhanced.sh
rm -f fix-*.sh
rm -f quick-*.sh

# Remove temporary Python files
echo "Removing temporary Python files..."
rm -f main_hotfix.py
rm -f main_enhanced.py
rm -f main_unified.py
rm -f main_tobermory.py
rm -f backend_local.py
rm -f backend_production.py
rm -f main_backend.py
rm -f test_main.py

# Remove old backend files
echo "Removing old backend files..."
rm -f backend_gcp*.py
rm -f backend_gcs*.py
rm -f backend_production*.py
rm -f backend_simple.py

# Clean up archive directory
echo "Cleaning archive directory..."
find archive -name "*.sh" -type f -delete 2>/dev/null || true
find archive -name "*.py" -type f -delete 2>/dev/null || true

# List remaining important files
echo -e "\n📁 Important files remaining:"
ls -la *.py *.yaml *.md 2>/dev/null | grep -v "^total"

echo -e "\n✅ Cleanup complete!"