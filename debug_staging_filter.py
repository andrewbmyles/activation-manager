#!/usr/bin/env python3
"""
Debug why filtering isn't working in staging
"""
import requests
import json

STAGING_URL = "https://enhanced-filter-20250530-134221-dot-feisty-catcher-461000-g2.nn.r.appspot.com"

# Test with very specific parameters
payload = {
    "query": "contact with friends household income",
    "top_k": 50,
    "filter_similar": True,
    "use_advanced_processing": False,
    "use_semantic": False,
    "use_keyword": True,
    "similarity_threshold": 0.5,  # Very low threshold
    "max_similar_per_group": 1    # Only 1 per group
}

print(f"Testing staging URL: {STAGING_URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*70 + "\n")

resp = requests.post(
    f"{STAGING_URL}/api/enhanced-variable-picker/search",
    json=payload
)

if resp.status_code == 200:
    data = resp.json()
    results = data.get('results', [])
    
    print(f"Total results: {data.get('total_found', 0)}")
    print(f"Search methods: {data.get('search_methods', {})}")
    
    # Group by base pattern manually
    base_patterns = {}
    for r in results:
        desc = r.get('description', '')
        if 'Contact with friends' in desc:
            if ' - ' in desc:
                base = desc.split(' - ')[0]
            else:
                base = desc
            
            if base not in base_patterns:
                base_patterns[base] = []
            base_patterns[base].append(desc)
    
    if base_patterns:
        print(f"\nFound {sum(len(v) for v in base_patterns.values())} 'Contact with friends' variables")
        print("\nGrouped by base pattern:")
        for base, variations in base_patterns.items():
            print(f"\n'{base}': {len(variations)} variations")
            for i, var in enumerate(variations[:3]):
                print(f"  {i+1}. {var}")
            if len(variations) > 3:
                print(f"  ... and {len(variations)-3} more")
    else:
        print("\nNo 'Contact with friends' variables found")
        
    # Check what we got instead
    print("\nFirst 5 results:")
    for i, r in enumerate(results[:5]):
        print(f"{i+1}. {r.get('description', 'N/A')}")
        
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)