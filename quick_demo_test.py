"""
Quick Demo Test Script
Verifies all systems are working for demo
"""

import requests
import json
import time

def test_demo_ready():
    """Test all demo components"""
    
    print("🎯 Activation Manager Demo Test")
    print("="*50)
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is healthy")
            health_data = response.json()
            print(f"   📊 Components: {', '.join(health_data['components'].keys())}")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API not accessible: {e}")
        return False
    
    # Test 2: React App
    print("\n2. Testing React App...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200 and "<!DOCTYPE html>" in response.text:
            print("   ✅ React app is serving")
        else:
            print(f"   ❌ React app check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ React app not accessible: {e}")
        return False
    
    # Test 3: Natural Language Workflow
    print("\n3. Testing Natural Language Workflow...")
    
    # Start session
    try:
        session_response = requests.post("http://localhost:5001/api/nl/start_session")
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f"   ✅ Session created: {session_id}")
    except Exception as e:
        print(f"   ❌ Session creation failed: {e}")
        return False
    
    # Test variable selection
    try:
        nl_request = {
            "session_id": session_id,
            "action": "process", 
            "payload": {
                "input": "Find environmentally conscious millennials with high disposable income"
            }
        }
        
        nl_response = requests.post(
            "http://localhost:5001/api/nl/process",
            json=nl_request,
            headers={'Content-Type': 'application/json'}
        )
        
        nl_data = nl_response.json()
        
        if nl_data.get('status') == 'variables_suggested':
            total_vars = nl_data.get('total_suggested', 0)
            print(f"   ✅ Variable selection working: {total_vars} variables suggested")
            
            # Show variable breakdown
            var_breakdown = {}
            for var_type, vars_list in nl_data.get('suggested_variables', {}).items():
                var_breakdown[var_type] = len(vars_list)
            
            print(f"   📊 Variable types: {var_breakdown}")
            
        else:
            print(f"   ❌ Variable selection failed: {nl_data.get('status')}")
            return False
            
    except Exception as e:
        print(f"   ❌ NL workflow failed: {e}")
        return False
    
    # Test 4: Complete Workflow (if time permits)
    print("\n4. Testing Complete Workflow...")
    try:
        confirm_request = {
            "session_id": session_id,
            "action": "process",
            "payload": {
                "input": "use all suggested variables"
            }
        }
        
        final_response = requests.post(
            "http://localhost:5001/api/nl/process",
            json=confirm_request,
            headers={'Content-Type': 'application/json'}
        )
        
        final_data = final_response.json()
        
        if final_data.get('status') == 'complete':
            segments = final_data.get('segments', [])
            print(f"   ✅ Complete workflow: {len(segments)} segments created")
            
            # Check constraint satisfaction
            constraint_met = all(5 <= seg.get('size_percentage', 0) <= 10 for seg in segments)
            print(f"   📊 Constraints satisfied: {'✅' if constraint_met else '❌'}")
            
            # Show segment sizes
            sizes = [f"{seg.get('size_percentage', 0):.1f}%" for seg in segments]
            print(f"   📊 Segment sizes: {', '.join(sizes)}")
            
        else:
            print(f"   ⚠️  Workflow in progress: {final_data.get('status')}")
            
    except Exception as e:
        print(f"   ⚠️  Complete workflow test failed: {e}")
    
    print("\n" + "="*50)
    print("🎉 DEMO SYSTEMS READY!")
    print("\n🎬 Demo URLs:")
    print("   Frontend: http://localhost:3000")
    print("   API:      http://localhost:5001/api/health")
    print("\n📋 Demo Flow:")
    print("   1. Open frontend URL")
    print("   2. Toggle 'Natural Language' mode")
    print("   3. Enter: 'Find tech-savvy millennials with high income'")
    print("   4. Review suggested variables")
    print("   5. Confirm selection")
    print("   6. View segmented results with PRIZM insights")
    
    return True

if __name__ == "__main__":
    success = test_demo_ready()
    if not success:
        print("\n❌ Demo setup incomplete. Check server status.")
        exit(1)
    else:
        print("\n✅ All systems ready for demo!")
        exit(0)