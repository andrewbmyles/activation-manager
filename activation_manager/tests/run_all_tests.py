"""
Comprehensive test runner for Audience Builder system
Executes all unit tests and logs any bugs found
"""

import unittest
import sys
import os
import traceback
import json
from datetime import datetime
from io import StringIO

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

# Import all test modules
test_modules = [
    'test_enhanced_variable_selector',
    'test_prizm_analyzer', 
    'test_constrained_k_medians',
    'test_data_retriever',
    'test_integrated_audience_handler',
    'test_unified_api'
]

class BugLogger:
    """Logs bugs and test failures for record keeping"""
    
    def __init__(self):
        self.bugs = []
        self.test_results = {}
        self.start_time = datetime.now()
    
    def log_bug(self, test_name, bug_type, description, traceback_str=None):
        """Log a bug with details"""
        bug = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'bug_type': bug_type,
            'description': description,
            'traceback': traceback_str,
            'severity': self._determine_severity(bug_type, description)
        }
        self.bugs.append(bug)
    
    def _determine_severity(self, bug_type, description):
        """Determine bug severity"""
        if bug_type in ['Error', 'Exception']:
            return 'HIGH'
        elif 'constraint' in description.lower() or 'data' in description.lower():
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def log_test_result(self, module_name, passed, failed, errors, skipped):
        """Log test results for a module"""
        self.test_results[module_name] = {
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'total': passed + failed + errors + skipped
        }
    
    def generate_report(self):
        """Generate comprehensive bug report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'test_execution': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'modules_tested': len(self.test_results)
            },
            'summary': {
                'total_bugs': len(self.bugs),
                'high_severity': len([b for b in self.bugs if b['severity'] == 'HIGH']),
                'medium_severity': len([b for b in self.bugs if b['severity'] == 'MEDIUM']),
                'low_severity': len([b for b in self.bugs if b['severity'] == 'LOW'])
            },
            'test_results': self.test_results,
            'bugs': self.bugs
        }
        
        return report
    
    def save_report(self, filename='bug_report.json'):
        """Save bug report to file"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename


class CustomTestResult(unittest.TestResult):
    """Custom test result class to capture detailed information"""
    
    def __init__(self, bug_logger, module_name):
        super().__init__()
        self.bug_logger = bug_logger
        self.module_name = module_name
        self.passed_tests = []
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_tests.append(str(test))
    
    def addError(self, test, err):
        super().addError(test, err)
        exc_type, exc_value, exc_traceback = err
        
        self.bug_logger.log_bug(
            test_name=str(test),
            bug_type='Error',
            description=str(exc_value),
            traceback_str=traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        exc_type, exc_value, exc_traceback = err
        
        self.bug_logger.log_bug(
            test_name=str(test),
            bug_type='Failure',
            description=str(exc_value),
            traceback_str=traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        
        # Log skipped tests as informational
        self.bug_logger.log_bug(
            test_name=str(test),
            bug_type='Skipped',
            description=f"Test skipped: {reason}",
            traceback_str=None
        )


def run_tests_for_module(module_name, bug_logger):
    """Run tests for a specific module"""
    print(f"\n{'='*60}")
    print(f"Testing Module: {module_name}")
    print('='*60)
    
    try:
        # Import the test module
        test_module = __import__(module_name)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Create custom test result
        result = CustomTestResult(bug_logger, module_name)
        
        # Capture stdout to show progress
        original_stdout = sys.stdout
        output_buffer = StringIO()
        sys.stdout = output_buffer
        
        try:
            # Run the tests
            suite.run(result)
        finally:
            sys.stdout = original_stdout
        
        # Print results
        passed = len(result.passed_tests)
        failed = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped)
        total = passed + failed + errors + skipped
        
        print(f"Results: {passed} passed, {failed} failed, {errors} errors, {skipped} skipped")
        print(f"Total tests: {total}")
        
        # Log results
        bug_logger.log_test_result(module_name, passed, failed, errors, skipped)
        
        # Show any failures/errors immediately
        if result.failures:
            print(f"\n❌ Failures in {module_name}:")
            for test, traceback_str in result.failures:
                print(f"  - {test}")
                print(f"    {traceback_str.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n🚨 Errors in {module_name}:")
            for test, traceback_str in result.errors:
                print(f"  - {test}")
                lines = traceback_str.split('\n')
                error_line = lines[-2].strip() if len(lines) > 1 else traceback_str.strip()
                print(f"    {error_line}")
        
        return result
        
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        bug_logger.log_bug(
            test_name=f"{module_name} (import)",
            bug_type='ImportError',
            description=str(e),
            traceback_str=traceback.format_exc()
        )
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error in {module_name}: {e}")
        bug_logger.log_bug(
            test_name=f"{module_name} (execution)",
            bug_type='UnexpectedError',
            description=str(e),
            traceback_str=traceback.format_exc()
        )
        return None


def main():
    """Main test execution function"""
    print("🧪 Starting Comprehensive Test Suite for Audience Builder")
    print("="*70)
    
    # Initialize bug logger
    bug_logger = BugLogger()
    
    # Track overall results
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    
    # Run tests for each module
    for module_name in test_modules:
        result = run_tests_for_module(module_name, bug_logger)
        
        if result:
            total_passed += len(result.successes) if hasattr(result, 'successes') else len(result.passed_tests)
            total_failed += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
    
    # Print final summary
    print("\n" + "="*70)
    print("🏁 FINAL TEST SUMMARY")
    print("="*70)
    print(f"Total Tests Run: {total_passed + total_failed + total_errors + total_skipped}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"🚨 Errors: {total_errors}")
    print(f"⏭️  Skipped: {total_skipped}")
    
    # Generate and save bug report
    report_file = bug_logger.save_report('bug_report.json')
    print(f"\n📋 Bug report saved to: {report_file}")
    
    # Print bug summary
    bugs = bug_logger.bugs
    if bugs:
        print(f"\n🐛 BUGS FOUND: {len(bugs)}")
        
        high_severity = [b for b in bugs if b['severity'] == 'HIGH']
        medium_severity = [b for b in bugs if b['severity'] == 'MEDIUM']
        low_severity = [b for b in bugs if b['severity'] == 'LOW']
        
        if high_severity:
            print(f"\n🔴 HIGH SEVERITY BUGS ({len(high_severity)}):")
            for bug in high_severity:
                print(f"  - {bug['test_name']}: {bug['description']}")
        
        if medium_severity:
            print(f"\n🟡 MEDIUM SEVERITY BUGS ({len(medium_severity)}):")
            for bug in medium_severity:
                print(f"  - {bug['test_name']}: {bug['description']}")
        
        if low_severity:
            print(f"\n🟢 LOW SEVERITY BUGS ({len(low_severity)}):")
            for bug in low_severity:
                print(f"  - {bug['test_name']}: {bug['description']}")
    else:
        print("\n🎉 NO BUGS FOUND! All tests passed successfully.")
    
    # Return exit code
    if total_failed > 0 or total_errors > 0:
        print("\n❌ Some tests failed. See bug report for details.")
        return 1
    else:
        print("\n✅ All tests passed successfully!")
        return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)