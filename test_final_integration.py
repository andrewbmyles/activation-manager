#!/usr/bin/env python3
"""
Final integration test to confirm all fixes work
"""
import time
import subprocess
import requests
import os
import sys

print("🧪 Final Integration Test - Enhanced Variable Picker Fix")
print("=" * 60)

# Kill any existing processes
subprocess.run(["pkill", "-f", "python main.py"], capture_output=True)
time.sleep(1)

print("\n🚀 Starting server with default settings...")
server = subprocess.Popen(
    ["python", "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Monitor startup
print("⏳ Waiting for server to start...")
start_time = time.time()
server_ready = False

# Read output for 15 seconds
while time.time() - start_time < 15:
    line = server.stdout.readline()
    if line:
        if "App ready to handle requests" in line or "Running on http" in line:
            server_ready = True
            print("✅ Server started successfully")
            break

if not server_ready:
    print("❌ Server failed to start")
    # Print last few lines
    for _ in range(10):
        line = server.stdout.readline()
        if line:
            print(f"  {line.strip()}")
    server.terminate()
    sys.exit(1)

# Wait for full initialization
time.sleep(3)

# Run test suite
tests = [
    {
        "name": "Health Check",
        "method": "GET",
        "url": "http://localhost:8080/health",
        "expected_status": 200
    },
    {
        "name": "Enhanced Variable Search",
        "method": "POST",
        "url": "http://localhost:8080/api/enhanced-variable-picker/search",
        "json": {"query": "high income millennials", "top_k": 10, "filter_similar": True},
        "expected_status": 200,
        "check_response": True
    },
    {
        "name": "Complex Query Search",
        "method": "POST",
        "url": "http://localhost:8080/api/variable-picker/search/complex",
        "json": {"query": "environmentally conscious women with high disposable income in urban areas", "limit": 20},
        "expected_status": 200,
        "check_response": True
    },
    {
        "name": "Variable Refine",
        "method": "POST",
        "url": "http://localhost:8080/api/variable-picker/refine",
        "json": {
            "description": "expand to include more demographic variables",
            "current_variables": ["AGE_25_34", "INCOME_100K_PLUS"],
            "mode": "expand"
        },
        "expected_status": 200
    },
    {
        "name": "Variable Categories",
        "method": "GET",
        "url": "http://localhost:8080/api/variable-picker/categories",
        "expected_status": 200
    },
    {
        "name": "Enhanced Stats",
        "method": "GET",
        "url": "http://localhost:8080/api/enhanced-variable-picker/stats",
        "expected_status": 200
    }
]

print(f"\n📋 Running {len(tests)} tests...")
passed = 0
failed = 0

for test in tests:
    try:
        print(f"\n  Testing: {test['name']}...")
        
        if test['method'] == 'GET':
            response = requests.get(test['url'], timeout=10)
        else:
            response = requests.post(
                test['url'],
                json=test.get('json', {}),
                timeout=10
            )
        
        if response.status_code == test['expected_status']:
            print(f"    ✅ Status: {response.status_code}")
            
            if test.get('check_response') and response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    print(f"    📊 Results: {len(data.get('results', []))}")
                    print(f"    🔍 Total found: {data.get('total_found', 0)}")
                    
                    # Show first result
                    if data.get('results'):
                        first = data['results'][0]
                        print(f"    📌 First result: {first.get('code')} - {first.get('description', '')[:50]}...")
            passed += 1
        else:
            print(f"    ❌ Failed: Expected {test['expected_status']}, got {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            failed += 1
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        failed += 1

# Test summary
print(f"\n📊 Test Results:")
print(f"  ✅ Passed: {passed}/{len(tests)}")
print(f"  ❌ Failed: {failed}/{len(tests)}")

# Cleanup
print("\n🧹 Stopping server...")
server.terminate()
try:
    server.wait(timeout=5)
except:
    server.kill()

if failed == 0:
    print("\n🎉 All tests passed! The enhanced variable picker fix is working correctly.")
else:
    print(f"\n⚠️ {failed} tests failed. Please review the errors above.")

print("\n" + "=" * 60)
print("Final integration test complete!")