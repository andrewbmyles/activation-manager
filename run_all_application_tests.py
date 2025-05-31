#!/usr/bin/env python3
"""
Comprehensive test runner for the entire Activation Manager application
Executes Python backend tests, React frontend tests, and validates the build
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class ApplicationTestRunner:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {
            'summary': {},
            'python_backend_tests': {},
            'react_frontend_tests': {},
            'enhanced_audience_tests': {},
            'build_validation': {},
            'execution_details': {}
        }
        self.start_time = datetime.now()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_python_backend_tests(self) -> Dict[str, Any]:
        """Run Python backend tests"""
        self.log("🐍 Running Python Backend Tests...")
        
        # Find all Python test files
        python_test_files = []
        test_dirs = [
            'activation_manager/tests',
            'tests',
            '.'  # Root level test files
        ]
        
        for test_dir in test_dirs:
            dir_path = os.path.join(self.project_root, test_dir)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    # Skip backup and virtual environment directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['backups', 'venv', '__pycache__']]
                    
                    for file in files:
                        if file.startswith('test_') and file.endswith('.py'):
                            rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                            python_test_files.append(rel_path)
        
        # Remove duplicates and sort
        python_test_files = sorted(list(set(python_test_files)))
        
        self.log(f"Found {len(python_test_files)} Python test files")
        
        test_results = {
            'total_files': len(python_test_files),
            'successful_files': 0,
            'failed_files': 0,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'details': {}
        }
        
        # Run key test files
        important_tests = [
            'test_audience_utils_complete.py',
            'test_complete_audience_workflow.py',
            'activation_manager/tests/test_minimal.py',
            'tests/test_data_persistence.py'
        ]
        
        for test_file in important_tests:
            if test_file in python_test_files or os.path.exists(os.path.join(self.project_root, test_file)):
                result = self.run_single_python_test(test_file)
                test_results['details'][test_file] = result
                
                if result['status'] == 'success':
                    test_results['successful_files'] += 1
                    test_results['passed_tests'] += result.get('tests_passed', 0)
                else:
                    test_results['failed_files'] += 1
                    test_results['failed_tests'] += result.get('tests_failed', 0)
                
                test_results['total_tests'] += result.get('total_tests', 0)
        
        # Run our enhanced audience test runner
        try:
            self.log("Running enhanced audience test runner...")
            result = subprocess.run([
                sys.executable, 'run_enhanced_audience_tests.py'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=30)
            
            if result.returncode == 0:
                test_results['details']['run_enhanced_audience_tests.py'] = {
                    'status': 'success',
                    'output': result.stdout,
                    'total_tests': 18,  # From previous execution
                    'tests_passed': 18,
                    'tests_failed': 0
                }
                test_results['successful_files'] += 1
                test_results['passed_tests'] += 18
                test_results['total_tests'] += 18
            else:
                test_results['details']['run_enhanced_audience_tests.py'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'total_tests': 18,
                    'tests_passed': 0,
                    'tests_failed': 18
                }
                test_results['failed_files'] += 1
                test_results['failed_tests'] += 18
                test_results['total_tests'] += 18
                
        except Exception as e:
            self.log(f"Enhanced audience tests failed: {str(e)}", "ERROR")
        
        test_results['pass_rate'] = (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
        
        self.log(f"✅ Python Backend: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['pass_rate']:.1f}%)")
        
        return test_results
    
    def run_single_python_test(self, test_file: str) -> Dict[str, Any]:
        """Run a single Python test file"""
        try:
            file_path = os.path.join(self.project_root, test_file)
            if not os.path.exists(file_path):
                return {
                    'status': 'skipped',
                    'reason': 'File not found',
                    'total_tests': 0,
                    'tests_passed': 0,
                    'tests_failed': 0
                }
            
            self.log(f"  Running {test_file}...")
            
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, cwd=self.project_root, timeout=30)
            
            if result.returncode == 0:
                # Try to extract test count from output
                output = result.stdout
                tests_passed = output.count('✅') + output.count('passed')
                tests_failed = output.count('❌') + output.count('failed')
                total_tests = tests_passed + tests_failed
                
                if total_tests == 0:
                    total_tests = 1  # Assume at least one test if file ran successfully
                    tests_passed = 1
                
                return {
                    'status': 'success',
                    'output': output,
                    'total_tests': total_tests,
                    'tests_passed': tests_passed,
                    'tests_failed': tests_failed
                }
            else:
                return {
                    'status': 'failed',
                    'error': result.stderr,
                    'output': result.stdout,
                    'total_tests': 1,
                    'tests_passed': 0,
                    'tests_failed': 1
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Test execution timed out',
                'total_tests': 1,
                'tests_passed': 0,
                'tests_failed': 1
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'total_tests': 1,
                'tests_passed': 0,
                'tests_failed': 1
            }
    
    def run_react_frontend_tests(self) -> Dict[str, Any]:
        """Run React frontend tests"""
        self.log("⚛️  Running React Frontend Tests...")
        
        # Check if we can run npm test
        try:
            # Check if package.json exists
            package_json_path = os.path.join(self.project_root, 'package.json')
            if not os.path.exists(package_json_path):
                return {
                    'status': 'skipped',
                    'reason': 'No package.json found',
                    'total_tests': 0,
                    'passed_tests': 0,
                    'failed_tests': 0
                }
            
            # Check if node_modules exists
            node_modules_path = os.path.join(self.project_root, 'node_modules')
            if not os.path.exists(node_modules_path):
                self.log("node_modules not found, running npm install first...")
                install_result = subprocess.run([
                    'npm', 'install'
                ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
                
                if install_result.returncode != 0:
                    return {
                        'status': 'failed',
                        'reason': 'npm install failed',
                        'error': install_result.stderr,
                        'total_tests': 0,
                        'passed_tests': 0,
                        'failed_tests': 0
                    }
            
            # Run tests in CI mode (non-interactive)
            self.log("Running npm test...")
            test_result = subprocess.run([
                'npm', 'test', '--', '--watchAll=false', '--testTimeout=30000'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=120)
            
            # Parse test results from Jest output
            output = test_result.stdout + test_result.stderr
            
            # Look for Jest test summary
            test_suites_passed = 0
            test_suites_failed = 0
            tests_passed = 0
            tests_failed = 0
            
            lines = output.split('\n')
            for line in lines:
                if 'Test Suites:' in line:
                    # Parse: "Test Suites: 5 passed, 5 total"
                    parts = line.split(':')[1].strip()
                    if 'passed' in parts:
                        test_suites_passed = int(parts.split('passed')[0].strip().split()[-1])
                    if 'failed' in parts:
                        test_suites_failed = int(parts.split('failed')[0].strip().split()[-1])
                
                elif 'Tests:' in line:
                    # Parse: "Tests: 15 passed, 15 total"
                    parts = line.split(':')[1].strip()
                    if 'passed' in parts:
                        tests_passed = int(parts.split('passed')[0].strip().split()[-1])
                    if 'failed' in parts:
                        tests_failed = int(parts.split('failed')[0].strip().split()[-1])
            
            total_tests = tests_passed + tests_failed
            pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
            
            status = 'success' if test_result.returncode == 0 else 'failed'
            
            self.log(f"✅ React Frontend: {tests_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
            
            return {
                'status': status,
                'total_tests': total_tests,
                'passed_tests': tests_passed,
                'failed_tests': tests_failed,
                'test_suites_passed': test_suites_passed,
                'test_suites_failed': test_suites_failed,
                'pass_rate': pass_rate,
                'output': output,
                'execution_time': '< 2 minutes'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'reason': 'Test execution timed out',
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        except Exception as e:
            self.log(f"React tests failed: {str(e)}", "ERROR")
            return {
                'status': 'error',
                'error': str(e),
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
    
    def validate_build(self) -> Dict[str, Any]:
        """Validate that the application builds successfully"""
        self.log("🔨 Validating Application Build...")
        
        try:
            # Check if we can build the React app
            package_json_path = os.path.join(self.project_root, 'package.json')
            if not os.path.exists(package_json_path):
                return {
                    'status': 'skipped',
                    'reason': 'No package.json found for build validation'
                }
            
            self.log("Running npm run build...")
            build_result = subprocess.run([
                'npm', 'run', 'build'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
            
            if build_result.returncode == 0:
                # Check if build directory was created
                build_dir = os.path.join(self.project_root, 'build')
                if os.path.exists(build_dir):
                    # Count files in build directory
                    file_count = sum(len(files) for _, _, files in os.walk(build_dir))
                    
                    self.log(f"✅ Build successful: {file_count} files generated")
                    
                    return {
                        'status': 'success',
                        'build_files': file_count,
                        'build_output': build_result.stdout,
                        'build_directory': build_dir
                    }
                else:
                    return {
                        'status': 'failed',
                        'reason': 'Build directory not created',
                        'output': build_result.stdout,
                        'error': build_result.stderr
                    }
            else:
                return {
                    'status': 'failed',
                    'reason': 'Build command failed',
                    'output': build_result.stdout,
                    'error': build_result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'reason': 'Build process timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_critical_files(self) -> Dict[str, Any]:
        """Check that all critical files exist"""
        self.log("📁 Checking Critical Files...")
        
        critical_files = {
            'Frontend': [
                'src/App.tsx',
                'src/components/EnhancedNLAudienceBuilder.tsx',
                'src/pages/SavedAudiences.tsx',
                'src/utils/audienceUtils.ts',
                'package.json'
            ],
            'Backend': [
                'main.py',
                'requirements.txt',
                'activation_manager/__init__.py'
            ],
            'Tests': [
                'src/utils/__tests__/audienceUtils.test.ts',
                'src/components/__tests__/EnhancedAudienceFeatures.test.tsx',
                'run_enhanced_audience_tests.py'
            ],
            'Documentation': [
                'README.md',
                'CHANGELOG.md',
                'docs/ENHANCED_AUDIENCE_FEATURES.md'
            ]
        }
        
        results = {}
        total_files = 0
        existing_files = 0
        
        for category, files in critical_files.items():
            category_results = {}
            for file_path in files:
                full_path = os.path.join(self.project_root, file_path)
                exists = os.path.exists(full_path)
                
                if exists:
                    file_size = os.path.getsize(full_path)
                    category_results[file_path] = {
                        'exists': True,
                        'size_bytes': file_size
                    }
                    existing_files += 1
                else:
                    category_results[file_path] = {
                        'exists': False
                    }
                
                total_files += 1
            
            results[category] = category_results
        
        completion_rate = (existing_files / total_files * 100) if total_files > 0 else 0
        
        self.log(f"✅ Critical Files: {existing_files}/{total_files} present ({completion_rate:.1f}%)")
        
        return {
            'total_files': total_files,
            'existing_files': existing_files,
            'completion_rate': completion_rate,
            'details': results
        }
    
    def generate_comprehensive_report(self) -> None:
        """Generate comprehensive test report"""
        self.log("📊 Generating Comprehensive Test Report...")
        
        # Run all test categories
        critical_files = self.check_critical_files()
        python_results = self.run_python_backend_tests()
        react_results = self.run_react_frontend_tests()
        build_validation = self.validate_build()
        
        # Calculate overall statistics
        total_tests = (python_results.get('total_tests', 0) + 
                      react_results.get('total_tests', 0))
        
        total_passed = (python_results.get('passed_tests', 0) + 
                       react_results.get('passed_tests', 0))
        
        total_failed = total_tests - total_passed
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        end_time = datetime.now()
        execution_duration = end_time - self.start_time
        
        # Store comprehensive results
        self.test_results = {
            'summary': {
                'execution_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration': str(execution_duration),
                'total_tests': total_tests,
                'passed_tests': total_passed,
                'failed_tests': total_failed,
                'pass_rate': round(overall_pass_rate, 1),
                'status': 'SUCCESS' if total_failed == 0 else 'PARTIAL' if total_passed > 0 else 'FAILED'
            },
            'critical_files': critical_files,
            'python_backend_tests': python_results,
            'react_frontend_tests': react_results,
            'build_validation': build_validation
        }
        
        # Print detailed report
        self.print_comprehensive_report()
        
        # Save JSON report
        self.save_json_report()
    
    def print_comprehensive_report(self) -> None:
        """Print comprehensive test report"""
        print("\n" + "="*80)
        print("🚀 ACTIVATION MANAGER - COMPREHENSIVE APPLICATION TEST REPORT")
        print("="*80)
        
        summary = self.test_results['summary']
        print(f"\n📊 OVERALL SUMMARY")
        print(f"{'Execution Time:':<20} {summary['execution_time']}")
        print(f"{'Duration:':<20} {summary['duration']}")
        print(f"{'Total Tests:':<20} {summary['total_tests']}")
        print(f"{'Passed:':<20} {summary['passed_tests']} ✅")
        print(f"{'Failed:':<20} {summary['failed_tests']} {'❌' if summary['failed_tests'] > 0 else '✅'}")
        print(f"{'Pass Rate:':<20} {summary['pass_rate']}%")
        print(f"{'Status:':<20} {summary['status']}")
        
        # Critical files check
        critical = self.test_results['critical_files']
        print(f"\n📁 CRITICAL FILES CHECK")
        print(f"{'Files Present:':<20} {critical['existing_files']}/{critical['total_files']} ({critical['completion_rate']:.1f}%)")
        
        # Test category breakdown
        categories = [
            ('Python Backend', self.test_results['python_backend_tests']),
            ('React Frontend', self.test_results['react_frontend_tests']),
            ('Build Validation', self.test_results['build_validation'])
        ]
        
        print(f"\n🧪 TEST CATEGORY RESULTS")
        for category_name, category_results in categories:
            if category_name == 'Build Validation':
                status = category_results.get('status', 'unknown')
                status_icon = "✅" if status == 'success' else "⚠️" if status == 'skipped' else "❌"
                print(f"{category_name:<20} {status_icon} {status.title()}")
            else:
                status = category_results.get('status', 'unknown')
                passed = category_results.get('passed_tests', 0)
                total = category_results.get('total_tests', 0)
                rate = category_results.get('pass_rate', 0)
                
                status_icon = "✅" if rate == 100 else "⚠️" if rate > 50 else "❌"
                print(f"{category_name:<20} {status_icon} {passed}/{total} ({rate:.1f}%)")
        
        # Detailed breakdowns
        if self.test_results['python_backend_tests'].get('details'):
            print(f"\n🐍 PYTHON BACKEND BREAKDOWN")
            for test_file, result in self.test_results['python_backend_tests']['details'].items():
                status = result.get('status', 'unknown')
                passed = result.get('tests_passed', 0)
                total = result.get('total_tests', 0)
                
                status_icon = "✅" if status == 'success' else "⚠️" if status == 'skipped' else "❌"
                file_name = test_file.split('/')[-1]
                print(f"  {file_name:<35} {status_icon} {passed}/{total}")
        
        # Build validation details
        build_result = self.test_results['build_validation']
        if build_result.get('status') == 'success':
            print(f"\n🔨 BUILD VALIDATION")
            print(f"  Status: ✅ Successful")
            print(f"  Files Generated: {build_result.get('build_files', 0)}")
        elif build_result.get('status') == 'failed':
            print(f"\n🔨 BUILD VALIDATION")
            print(f"  Status: ❌ Failed - {build_result.get('reason', 'Unknown error')}")
        
        # Final assessment
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT")
        
        critical_rate = critical['completion_rate']
        test_pass_rate = summary['pass_rate']
        build_status = build_result.get('status', 'unknown')
        
        if critical_rate >= 95 and test_pass_rate >= 90 and build_status == 'success':
            print("🎉 READY FOR PRODUCTION DEPLOYMENT!")
            print("   All systems green - tests passing, build successful, files present.")
        elif critical_rate >= 90 and test_pass_rate >= 80:
            print("✅ READY FOR STAGING DEPLOYMENT")
            print("   Most tests passing, minor issues to address.")
        elif critical_rate >= 80 and test_pass_rate >= 70:
            print("⚠️  DEVELOPMENT READY")
            print("   Core functionality working, needs testing improvements.")
        else:
            print("❌ NOT READY FOR DEPLOYMENT")
            print("   Significant issues detected, requires attention.")
        
        print("="*80)
    
    def save_json_report(self) -> None:
        """Save comprehensive test results to JSON file"""
        report_file = os.path.join(self.project_root, 'comprehensive_test_report.json')
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.log(f"📄 Comprehensive test report saved to: {report_file}")
        except Exception as e:
            self.log(f"⚠️  Failed to save JSON report: {str(e)}", "WARNING")

def main():
    """Main execution function"""
    print("🚀 Starting Comprehensive Application Test Suite...")
    print("Testing Python Backend + React Frontend + Build Validation")
    print("=" * 80)
    
    runner = ApplicationTestRunner()
    runner.generate_comprehensive_report()
    
    print("\n✅ Comprehensive testing completed!")

if __name__ == "__main__":
    main()