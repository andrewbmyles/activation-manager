#!/usr/bin/env python3
"""
Script to organize test files from root directory into proper test structure
"""
import os
import shutil
from pathlib import Path
import re

def categorize_test_file(filename, content):
    """Determine which category a test file belongs to"""
    
    # Read first few lines to understand test type
    lines = content.lower()
    
    # System/E2E tests
    if any(word in filename.lower() for word in ['deployment', 'full', 'system', 'e2e', 'staging', 'production']):
        return 'system'
    
    # Integration tests
    if any(word in filename.lower() for word in ['integration', 'api', 'workflow', 'complex']):
        return 'integration'
    
    # Check content for clues
    if 'requests.post' in lines or 'requests.get' in lines:
        return 'integration'
    
    if 'unittest' in lines or 'test_' in lines and 'def test_' in lines:
        return 'unit'
    
    # Default to unit tests
    return 'unit'

def organize_tests(dry_run=True):
    """Organize test files into proper directory structure"""
    
    # Create test directory structure
    test_dirs = {
        'unit': 'tests/unit',
        'integration': 'tests/integration', 
        'system': 'tests/system',
        'fixtures': 'tests/fixtures'
    }
    
    if not dry_run:
        for dir_path in test_dirs.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Find all test files in root
    root_path = Path('.')
    test_files = list(root_path.glob('test_*.py'))
    
    moves = []
    
    for test_file in test_files:
        # Skip if already in tests directory
        if 'tests' in test_file.parts:
            continue
            
        # Read file to categorize
        try:
            with open(test_file, 'r') as f:
                content = f.read()
        except:
            content = ""
        
        category = categorize_test_file(test_file.name, content)
        new_path = Path(test_dirs[category]) / test_file.name
        
        moves.append((test_file, new_path, category))
    
    # Print plan
    print("Test Organization Plan")
    print("=" * 70)
    print(f"Found {len(moves)} test files to organize\n")
    
    # Group by category
    by_category = {}
    for old, new, cat in moves:
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append((old, new))
    
    for category, files in by_category.items():
        print(f"\n{category.upper()} Tests ({len(files)} files):")
        print("-" * 50)
        for old, new in files[:5]:  # Show first 5
            print(f"  {old.name} → {new}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    
    if dry_run:
        print("\n" + "="*70)
        print("DRY RUN - No files moved")
        print("To execute, run: python organize_tests.py --execute")
    else:
        print("\n" + "="*70)
        print("Moving files...")
        
        moved = 0
        errors = []
        
        for old_path, new_path, _ in moves:
            try:
                shutil.move(str(old_path), str(new_path))
                moved += 1
            except Exception as e:
                errors.append((old_path, e))
        
        print(f"\n✅ Successfully moved {moved} files")
        
        if errors:
            print(f"\n❌ Failed to move {len(errors)} files:")
            for path, error in errors:
                print(f"  {path}: {error}")
        
        # Create __init__.py files
        for dir_path in test_dirs.values():
            init_file = Path(dir_path) / '__init__.py'
            init_file.touch()
        
        print("\n✅ Created __init__.py files in test directories")
        
        # Create a simple test runner
        create_test_runner()

def create_test_runner():
    """Create a test runner script"""
    
    runner_content = '''#!/usr/bin/env python3
"""
Test runner for Activation Manager
"""
import sys
import pytest

def main():
    """Run tests with appropriate arguments"""
    
    # Default pytest arguments
    args = [
        'tests/',
        '-v',  # Verbose
        '--tb=short',  # Short traceback format
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == '__main__':
    sys.exit(main())
'''
    
    with open('run_tests.py', 'w') as f:
        f.write(runner_content)
    
    os.chmod('run_tests.py', 0o755)
    print("✅ Created run_tests.py test runner")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        organize_tests(dry_run=False)
    else:
        organize_tests(dry_run=True)

if __name__ == '__main__':
    main()