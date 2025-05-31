#!/usr/bin/env python3
"""
Minimal Test Script - Tests functionality with minimal cost
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_basic_functionality():
    """Test basic API functionality without using Claude"""
    base_url = "http://localhost:5000"
    
    print("🧪 Running Minimal Cost Tests")
    print("="*40)
    
    # Test 1: Health check (no cost)
    print("\n1. Health Check:")
    try:
        resp = requests.get(f"{base_url}/api/health")
        print(f"   Status: {resp.status_code}")
        print(f"   API: {'✅ Running' if resp.json()['status'] == 'healthy' else '❌ Not healthy'}")
    except:
        print("   ❌ API not running. Start with: python start_demo.py")
        return
    
    # Test 2: Variable listing (no cost)
    print("\n2. Available Variables:")
    resp = requests.get(f"{base_url}/api/variables")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Total variables: {data['total_count']}")
        for var_type, vars in data['variables'].items():
            print(f"   - {var_type}: {len(vars)} variables")
    
    # Test 3: Variable selection (no Claude API cost)
    print("\n3. Variable Selection (no API cost):")
    resp = requests.post(
        f"{base_url}/api/variable_selector",
        json={"user_request": "millennials with high income"}
    )
    if resp.status_code == 200:
        suggestions = resp.json()['suggestions']
        print(f"   Found {len(suggestions)} relevant variables")
        for i, var in enumerate(suggestions[:3], 1):
            print(f"   {i}. {var['description']} (score: {var['score']})")
    
    # Test 4: Quick clustering test (100 records only)
    print("\n4. Clustering Test (100 records):")
    selected_vars = [s['code'] for s in suggestions[:5]]
    resp = requests.post(
        f"{base_url}/api/cluster_analyzer",
        json={
            "variable_codes": selected_vars,
            "sample_size": 100  # Minimal sample
        }
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"   Created {result['num_groups']} segments")
        for group in result['groups']:
            print(f"   - Segment {group['group_id']}: {group['percentage']}% ({group['size']} records)")
    
    print("\n✅ All tests completed!")
    print("\n💰 Cost Summary:")
    print("   - Claude API calls: 0")
    print("   - Records processed: 100")
    print("   - Estimated cost: $0.00")
    
    print("\n📝 Next Steps:")
    print("   1. Open the web interface")
    print("   2. Try a natural language query")
    print("   3. Claude will only be called when using chat/NLWeb features")

if __name__ == "__main__":
    test_basic_functionality()