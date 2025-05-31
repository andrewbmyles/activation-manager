#!/usr/bin/env python3
"""
Test runner for enhanced functionality
Runs all new tests and logs bugs found
"""

import os
import sys
import json
import unittest
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# Test modules to run
TEST_MODULES = [
    'test_enhanced_audience_api',
    'test_enhanced_variable_selector_v2',  # If exists
]

# Bug tracking
bugs_found = []

def run_python_tests():
    """Run Python unit tests"""
    print("🧪 Running Python Unit Tests...")
    print("=" * 60)
    
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Load tests
    for module_name in TEST_MODULES:
        try:
            module = __import__(f'tests.{module_name}', fromlist=[module_name])
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"✅ Loaded tests from {module_name}")
        except ImportError as e:
            print(f"⚠️  Could not load {module_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log failures
    if result.failures:
        for test, traceback in result.failures:
            bugs_found.append({
                'type': 'Python Test Failure',
                'test': str(test),
                'error': traceback,
                'severity': 'High'
            })
    
    if result.errors:
        for test, traceback in result.errors:
            bugs_found.append({
                'type': 'Python Test Error',
                'test': str(test),
                'error': traceback,
                'severity': 'Critical'
            })
    
    return result.wasSuccessful()

def run_react_tests():
    """Run React/TypeScript tests"""
    print("\n🧪 Running React Component Tests...")
    print("=" * 60)
    
    # Change to audience-manager directory
    react_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'audience-manager'
    )
    
    if not os.path.exists(react_dir):
        print("❌ React directory not found")
        return False
    
    try:
        # Run Jest tests
        result = subprocess.run(
            ['npm', 'test', '--', '--testPathPattern=EnhancedNLAudienceBuilder.test', '--watchAll=false'],
            cwd=react_dir,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(result.stderr)
            bugs_found.append({
                'type': 'React Test Failure',
                'test': 'EnhancedNLAudienceBuilder tests',
                'error': result.stderr or result.stdout,
                'severity': 'High'
            })
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error running React tests: {e}")
        bugs_found.append({
            'type': 'React Test Error',
            'test': 'Test execution',
            'error': str(e),
            'severity': 'Critical'
        })
        return False

def check_api_integration():
    """Check API integration"""
    print("\n🧪 Testing API Integration...")
    print("=" * 60)
    
    try:
        import requests
        
        # Check if API is running
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            print("✅ API is healthy")
            data = response.json()
            print(f"   Components: {data.get('components', {})}")
        else:
            print("⚠️  API health check failed")
            bugs_found.append({
                'type': 'API Integration',
                'test': 'Health check',
                'error': f'Status code: {response.status_code}',
                'severity': 'Medium'
            })
    
    except Exception as e:
        print(f"⚠️  Could not connect to API: {e}")
        print("   Make sure the API is running on port 5001")

def generate_bug_report():
    """Generate comprehensive bug report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_bugs': len(bugs_found),
        'by_severity': {
            'Critical': len([b for b in bugs_found if b['severity'] == 'Critical']),
            'High': len([b for b in bugs_found if b['severity'] == 'High']),
            'Medium': len([b for b in bugs_found if b['severity'] == 'Medium']),
            'Low': len([b for b in bugs_found if b['severity'] == 'Low'])
        },
        'bugs': bugs_found
    }
    
    # Save report
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f'enhanced_bug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Bug report saved to: {report_path}")
    
    # Print summary
    print("\n🐛 BUG SUMMARY")
    print("=" * 60)
    print(f"Total bugs found: {report['total_bugs']}")
    for severity, count in report['by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    if bugs_found:
        print("\n🔍 Bug Details:")
        for i, bug in enumerate(bugs_found, 1):
            print(f"\n{i}. {bug['type']} - {bug['severity']}")
            print(f"   Test: {bug['test']}")
            print(f"   Error: {bug['error'][:200]}...")

def main():
    """Run all tests and generate report"""
    print("🚀 Enhanced Functionality Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    python_success = run_python_tests()
    # react_success = run_react_tests()  # Commented out as it requires npm
    check_api_integration()
    
    # Generate report
    generate_bug_report()
    
    # Final status
    print("\n✅ TESTING COMPLETE")
    if len(bugs_found) == 0:
        print("🎉 All tests passed! No bugs found.")
        return 0
    else:
        print(f"❌ Found {len(bugs_found)} bugs that need fixing.")
        return 1

if __name__ == '__main__':
    sys.exit(main())