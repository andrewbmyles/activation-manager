"""
Demo script to test Audience Builder functionality
Shows how to use the system to create audience segments
"""

import json
from audience_builder import AudienceBuilder
from variable_catalog import get_full_catalog
import pandas as pd


def print_separator():
    print("\n" + "="*80 + "\n")


def demo_audience_builder():
    """
    Demonstrate the audience builder functionality
    """
    # Initialize the audience builder
    print("Initializing Audience Builder...")
    data_path = "/Users/myles/Documents/Activation Manager/Synthetic_Data/output/synthetic_consumer_data_1000_20250525_155201.csv"
    
    builder = AudienceBuilder(
        variable_catalog=get_full_catalog(),
        data_path=data_path
    )
    
    # Load the data
    print(f"Loading data from: {data_path}")
    builder.data_retriever.load_data()
    print(f"Data loaded: {builder.data_retriever.data.shape[0]} rows, {builder.data_retriever.data.shape[1]} columns")
    
    print_separator()
    
    # Test Case 1: Environmentally conscious millennials
    print("TEST CASE 1: Finding environmentally conscious millennials with high disposable income")
    print("User request: 'I need to find environmentally conscious millennials with high disposable income who live in urban areas'")
    
    user_request1 = "I need to find environmentally conscious millennials with high disposable income who live in urban areas for our new sustainable product line"
    
    # Step 1: Variable selection
    print("\nStep 1: Analyzing request and selecting variables...")
    suggestions = builder.variable_selector.analyze_request(user_request1)
    
    print(f"\nTop 10 suggested variables:")
    for i, var in enumerate(suggestions[:10], 1):
        print(f"{i}. {var['code']} - {var['description']} (Score: {var['score']})")
    
    # Simulate user confirmation of variables
    selected_vars = [var['code'] for var in suggestions[:7]]
    print(f"\nConfirming selection of {len(selected_vars)} variables: {', '.join(selected_vars[:3])}...")
    
    # Step 2: Build audience with clustering
    print("\nStep 2: Building audience segments with clustering...")
    results = builder.build_audience(user_request1, selected_vars)
    
    # Step 3: Get profiles
    print("\nStep 3: Analyzing group profiles...")
    profiles = builder.get_group_profiles()
    
    print_separator()
    print("AUDIENCE SEGMENTS CREATED:")
    
    for group_id, profile in profiles.items():
        print(f"\nGROUP {group_id}:")
        print(f"  Size: {profile['size']} records ({profile['percentage']}%)")
        print("  Key Characteristics:")
        
        # Show top 3 characteristics
        char_count = 0
        for var_code, stats in profile['characteristics'].items():
            if char_count >= 3:
                break
            if 'dominant_value' in stats:
                print(f"    - {var_code}: {stats['dominant_value']} ({stats['percentage']}%)")
            elif 'mean' in stats:
                print(f"    - {var_code}: Mean={stats['mean']:.2f}, Median={stats['median']:.2f}")
            char_count += 1
    
    print_separator()
    
    # Test Case 2: Different audience request
    print("TEST CASE 2: Finding tech-savvy urban professionals")
    print("User request: 'Find urban professionals with high income who are early technology adopters'")
    
    user_request2 = "Find urban professionals with high income who are early technology adopters interested in premium brands"
    
    suggestions2 = builder.variable_selector.analyze_request(user_request2)
    print(f"\nFound {len(suggestions2)} relevant variables")
    
    selected_vars2 = [var['code'] for var in suggestions2[:6]]
    print(f"Auto-selecting top {len(selected_vars2)} variables...")
    
    results2 = builder.build_audience(user_request2, selected_vars2)
    profiles2 = builder.get_group_profiles()
    
    print(f"\nCreated {len(profiles2)} audience segments")
    
    print_separator()
    
    # Save sample results
    print("Saving sample results to CSV...")
    sample_results = results.head(100)
    sample_results.to_csv('/Users/myles/Documents/Activation Manager/sample_audience_segments.csv', index=False)
    print("Sample saved to: sample_audience_segments.csv")
    
    # Generate summary report
    print("\nGENERATING SUMMARY REPORT:")
    print(f"Total records processed: {len(results)}")
    print(f"Number of segments created: {len(profiles)}")
    print(f"Variables used: {len(selected_vars)}")
    print(f"Clustering constraint: 5-10% per segment")
    
    # Check constraint satisfaction
    print("\nConstraint Validation:")
    for group_id, profile in profiles.items():
        pct = profile['percentage']
        status = "✓" if 5 <= pct <= 10 else "✗"
        print(f"  Group {group_id}: {pct}% {status}")


def test_api_endpoints():
    """
    Test the API endpoints (requires Flask server to be running)
    """
    print("\n" + "="*80)
    print("API ENDPOINT TESTS")
    print("="*80)
    
    print("\nTo test the API endpoints:")
    print("1. Run the Flask server: python audience_api.py")
    print("2. Use these curl commands:\n")
    
    # Variable selector test
    print("# Test variable selector:")
    print('''curl -X POST http://localhost:5000/api/variable_selector \\
  -H "Content-Type: application/json" \\
  -d '{"user_request": "environmentally conscious millennials with high income"}'
''')
    
    # Analyze endpoint test
    print("\n# Test complete analysis:")
    print('''curl -X POST http://localhost:5000/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"user_request": "urban millennials interested in sustainable products", "auto_select": true}'
''')
    
    # List variables test
    print("\n# List all variables:")
    print("curl http://localhost:5000/api/variables")


if __name__ == "__main__":
    print("AUDIENCE BUILDER DEMO")
    print("="*80)
    
    try:
        # Run the main demo
        demo_audience_builder()
        
        # Show API test commands
        test_api_endpoints()
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        import traceback
        traceback.print_exc()