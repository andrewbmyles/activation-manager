#!/usr/bin/env python3
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
