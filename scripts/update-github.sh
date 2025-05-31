#!/bin/bash
# Script to update GitHub with refactoring changes

echo "GitHub Update Script"
echo "==================="
echo
echo "This script will help you update GitHub with the refactoring changes."
echo

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Git not initialized in this directory"
    echo "Run: git init"
    exit 1
fi

# Show current status
echo "Current Git Status:"
echo "-------------------"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "... and $(( $(git status --short | wc -l) - 20 )) more files"
fi

echo
echo "Suggested commit process:"
echo "-------------------------"
echo
echo "1. Add the refactoring plan and documentation:"
echo "   git add REFACTORING_IMPLEMENTATION_SUMMARY.md"
echo "   git add REFACTORING_AND_DOCUMENTATION_PLAN.md"
echo "   git add .github/CONTRIBUTING.md"
echo "   git add .github/workflows/ci.yml"
echo "   git add docs/"
echo "   git commit -m 'docs: add refactoring plan and technical documentation'"
echo
echo "2. Add the test organization:"
echo "   git add tests/"
echo "   git add scripts/organize_tests.py"
echo "   git add run_tests.py"
echo "   git commit -m 'refactor: organize test files into proper structure'"
echo
echo "3. Add the deployment cleanup:"
echo "   git add scripts/deploy/"
echo "   git add scripts/archive/"
echo "   git add DEPLOYMENT_QUICK_GUIDE.md"
echo "   git commit -m 'refactor: consolidate deployment scripts'"
echo
echo "4. Update README and cleanup:"
echo "   git add README.md"
echo "   git add archive/"
echo "   git commit -m 'docs: update README with new project structure'"
echo
echo "5. Push to GitHub:"
echo "   git push origin main"
echo
echo "Would you like to create these commits now? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo
    echo "Creating commits..."
    
    # Commit 1: Documentation
    git add REFACTORING_IMPLEMENTATION_SUMMARY.md REFACTORING_AND_DOCUMENTATION_PLAN.md .github/ docs/
    git commit -m "docs: add refactoring plan and technical documentation

- Added comprehensive refactoring plan (4-week timeline)
- Created CONTRIBUTING.md with code standards
- Added GitHub Actions CI/CD workflow
- Created API reference and deployment guides
- Added technical documentation index"
    
    # Commit 2: Test organization
    git add tests/ scripts/organize_tests.py run_tests.py
    git commit -m "refactor: organize test files into proper structure

- Moved 52 test files from root to tests/ directory
- Organized into unit/, integration/, and system/ subdirectories
- Created test runner script
- Added __init__.py files for proper Python imports"
    
    # Commit 3: Deployment scripts
    git add scripts/deploy/ scripts/archive/ DEPLOYMENT_QUICK_GUIDE.md
    git commit -m "refactor: consolidate deployment scripts

- Reduced from 35 to 3 essential deployment scripts
- Archived old scripts for reference
- Created quick deployment guide
- Simplified deployment process"
    
    # Commit 4: README and cleanup
    git add README.md archive/
    git commit -m "docs: update README with new project structure

- Added project structure diagram
- Updated deployment instructions
- Added quick start section
- Added documentation links"
    
    echo
    echo "✅ Commits created!"
    echo
    echo "To push to GitHub:"
    echo "  git push origin main"
else
    echo
    echo "Skipping automatic commits. You can run the commands manually."
fi

echo
echo "Additional GitHub tasks:"
echo "------------------------"
echo "1. Create issue templates in .github/ISSUE_TEMPLATE/"
echo "2. Set up branch protection rules"
echo "3. Enable GitHub Actions"
echo "4. Update repository description and topics"
echo "5. Create a project board for tracking refactoring progress"