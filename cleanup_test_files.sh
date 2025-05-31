#!/bin/bash
# Cleanup script to organize test files and prepare for GitHub
# Date: May 30, 2025

echo "🧹 Cleaning up test files and organizing repository..."

# Create archive directory for test files
mkdir -p archive/test-files-20250530

# Move all temporary test files to archive
echo "📦 Archiving temporary test files..."
mv test_direct_fix.py archive/test-files-20250530/ 2>/dev/null
mv test_enhanced_crash.py archive/test-files-20250530/ 2>/dev/null
mv test_enhanced_picker_details.py archive/test-files-20250530/ 2>/dev/null
mv test_enhanced_picker_init.py archive/test-files-20250530/ 2>/dev/null
mv test_fixed_integration.py archive/test-files-20250530/ 2>/dev/null
mv test_fixed_main.py archive/test-files-20250530/ 2>/dev/null
mv test_integration_simple.py archive/test-files-20250530/ 2>/dev/null
mv test_preinit_fix.py archive/test-files-20250530/ 2>/dev/null
mv test_server_no_debug.py archive/test-files-20250530/ 2>/dev/null
mv test_server_with_fix.py archive/test-files-20250530/ 2>/dev/null
mv test_staging_fix.py archive/test-files-20250530/ 2>/dev/null
mv test_production_traffic.py archive/test-files-20250530/ 2>/dev/null
mv test_production_stability.py archive/test-files-20250530/ 2>/dev/null
mv test_comprehensive_fix.py archive/test-files-20250530/ 2>/dev/null
mv test_unified_migration.py archive/test-files-20250530/ 2>/dev/null
mv test_without_migration.py archive/test-files-20250530/ 2>/dev/null

# Keep only the essential test file
echo "✅ Keeping essential test: test_final_integration.py"

# Move deployment scripts to organized location
echo "📁 Organizing deployment scripts..."
mkdir -p scripts/deploy
mv deploy-unified-search-staging.sh scripts/deploy/ 2>/dev/null
mv fix-gcp-permissions.sh scripts/deploy/ 2>/dev/null

# Clean up temporary Python files
echo "🗑️  Removing temporary Python files..."
rm -f main_simplified_test.py
rm -f debug_enhanced_picker.py
rm -f qa_test_refactoring.py

# Clean up old deployment summaries (keeping the latest)
echo "📄 Archiving old deployment summaries..."
mkdir -p archive/deployment-summaries-20250530
mv DEPLOYMENT_SUCCESS.md archive/deployment-summaries-20250530/ 2>/dev/null
mv DEPLOYMENT_COMPLETE.md archive/deployment-summaries-20250530/ 2>/dev/null
mv DEPLOYMENT_LOG.md archive/deployment-summaries-20250530/ 2>/dev/null

# Move refactoring work documents to docs
echo "📚 Moving refactoring docs to proper location..."
mv REFACTORING_IMPLEMENTATION_SUMMARY.md docs/archive/ 2>/dev/null
mv WEEK3_FIXES_SUMMARY.md docs/archive/ 2>/dev/null
mv FIX_INTEGRATION_PLAN.md docs/archive/ 2>/dev/null
mv INTEGRATION_ANALYSIS.md docs/archive/ 2>/dev/null
mv DEBUG_FINDINGS.md docs/archive/ 2>/dev/null

# Clean up .pyc and __pycache__
echo "🧹 Cleaning Python cache files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Update .gitignore if needed
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Test files
test_*.py
!test_final_integration.py
archive/test-files-*/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# Local environment
.env.local
.env.*.local

# Temporary files
*.tmp
*.temp
*.log

# OS files
.DS_Store
Thumbs.db

# Deployment artifacts
.last_deployment
*.tar.gz
EOF

echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "- Archived temporary test files to: archive/test-files-20250530/"
echo "- Organized deployment scripts to: scripts/deploy/"
echo "- Moved documentation to: docs/archive/"
echo "- Updated .gitignore"
echo "- Kept essential files for production"

echo ""
echo "🎯 Next steps:"
echo "1. Review git status"
echo "2. Commit cleanup changes"
echo "3. Push to GitHub"