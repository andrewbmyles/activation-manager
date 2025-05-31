#!/usr/bin/env python
"""
Test runner for the Activation Manager
"""
import os
import sys
import subprocess

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("Running Activation Manager Tests")
    print("=" * 60)
    
    # Test the enhanced API directly
    print("\n1. Testing Enhanced Audience API...")
    try:
        # Import and test the API
        from api.enhanced_audience_api import app, data_retriever
        
        # Check if data is loaded
        if data_retriever.data is not None:
            print(f"✅ Data loaded successfully: {len(data_retriever.data)} records")
        else:
            print("❌ Data not loaded")
            
        # Test variable selector
        from core.enhanced_variable_selector_v2 import EnhancedVariableSelectorV2
        selector = EnhancedVariableSelectorV2()
        results = selector.analyze_request("environmentally conscious millennials")
        print(f"✅ Variable selector working: {len(results)} variables found")
        
        # Test clustering
        from core.audience_builder import ConstrainedKMedians
        clusterer = ConstrainedKMedians()
        print("✅ Clustering module loaded successfully")
        
        # Test PRIZM analyzer
        from core.prizm_analyzer import PRIZMAnalyzer
        analyzer = PRIZMAnalyzer()
        print("✅ PRIZM analyzer loaded successfully")
        
        print("\n✅ All core components are working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    # Test the React components
    print("\n2. Checking React Components...")
    react_test_file = os.path.join(
        os.path.dirname(__file__), 
        '../audience-manager/src/components/EnhancedNLAudienceBuilder.test.tsx'
    )
    if os.path.exists(react_test_file):
        print("✅ React test file exists")
    else:
        print("❌ React test file not found")
        
    # Check configuration
    print("\n3. Checking Configuration...")
    try:
        from config.settings import SYNTHETIC_DATA_PATH, API_PORT
        print(f"✅ Configuration loaded:")
        print(f"   - Data path: {SYNTHETIC_DATA_PATH}")
        print(f"   - API port: {API_PORT}")
        
        # Check if data file exists
        if os.path.exists(SYNTHETIC_DATA_PATH):
            file_size = os.path.getsize(SYNTHETIC_DATA_PATH) / (1024 * 1024 * 1024)  # GB
            print(f"   - Data file exists: {file_size:.2f} GB")
        else:
            print("   - ❌ Data file not found!")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        
    print("\n" + "=" * 60)
    print("Test Summary Complete")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()