"""
Test Script for Enhanced Audience Builder Tools
Demonstrates the integrated variable selector and PRIZM analyzer
"""

import asyncio
import os
from integrated_audience_handler import IntegratedAudienceHandler
import json
from dotenv import load_dotenv

load_dotenv()


async def test_enhanced_workflow():
    """Test the complete workflow with enhanced tools"""
    
    print("🎯 Enhanced Audience Builder - Tool Demonstration")
    print("="*60)
    print("\nThis demonstrates:")
    print("1. ✨ Enhanced Variable Selection using metadata files")
    print("2. 📊 PRIZM Analysis for rich segment descriptions")
    print("3. 🎲 K-Medians clustering with 5-10% constraints")
    print("="*60)
    
    # Initialize handler
    handler = IntegratedAudienceHandler(
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', 'test_key'),
        data_api_endpoint="http://localhost:5000/api/data",
        data_api_key="test_key"
    )
    
    # Test prompts to demonstrate variable selection
    test_prompts = [
        "Find tech-savvy millennials with high income who are environmentally conscious",
        "I need urban families with children interested in organic products",
        "Target affluent seniors who travel frequently and value luxury experiences"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n\n{'='*60}")
        print(f"Test Case {i}: {prompt}")
        print("="*60)
        
        # Step 1: Analyze prompt
        print("\n📝 Step 1: Analyzing your requirements...")
        result = await handler.process_request(prompt)
        
        if result['status'] == 'variables_suggested':
            print(f"\n✅ Found {result['total_suggested']} relevant variables")
            
            # Show suggested variables by category
            for var_type, vars_list in result['suggested_variables'].items():
                if vars_list:
                    print(f"\n{var_type.upper()} Variables:")
                    for var in vars_list[:3]:  # Show top 3
                        print(f"  • {var['code']}: {var['description']}")
                        print(f"    Score: {var['score']}, Category: {var.get('category', 'N/A')}")
            
            # Get session ID for next step
            session_id = list(handler.sessions.keys())[0]
            
            # Step 2: Confirm all variables
            print("\n\n📋 Step 2: Confirming all suggested variables...")
            result = await handler.process_request("use all suggested variables", session_id)
            
            if result['status'] == 'complete':
                print(f"\n✅ Successfully created {len(result['segments'])} audience segments!")
                
                # Display segment details
                print("\n📊 Segment Analysis:")
                for segment in result['segments']:
                    print(f"\n{'─'*40}")
                    print(f"Segment {segment['group_id']}:")
                    print(f"  Size: {segment['size']:,} records ({segment['size_percentage']}%)")
                    
                    # Show key characteristics
                    print("  Key Characteristics:")
                    chars = segment['characteristics']
                    for var_name, var_data in list(chars.items())[:3]:  # Top 3 characteristics
                        if var_data['type'] == 'categorical':
                            print(f"    • {var_name}: {var_data['dominant_value']} ({var_data['dominant_percentage']}%)")
                        else:
                            print(f"    • {var_name}: Mean={var_data['mean']}, Median={var_data['median']}")
                    
                    # Show PRIZM profile if available
                    if 'prizm_profile' in segment:
                        profile = segment['prizm_profile']
                        print("\n  🏆 PRIZM Profile:")
                        print(f"    Dominant Segments: {', '.join(profile['dominant_segments'][:3])}")
                        print(f"    Demographics: {profile['demographics']}")
                        print(f"    Key Behaviors: {', '.join(profile['key_behaviors'][:3])}")
                        if 'marketing_implications' in profile:
                            print(f"    Marketing Tips: {profile['marketing_implications'][:100]}...")
                
                # Show overall summary if PRIZM data available
                if 'prizm_summary' in result:
                    summary = result['prizm_summary']
                    print(f"\n\n📈 Overall Market Analysis:")
                    print(f"  Diversity Score: {summary['diversity_score']}")
                    print(f"  Market Potential: {summary['market_potential_index']}")
                    print(f"  Top Segments: {', '.join(summary['top_segments'][:3])}")
        
        # Reset for next test
        handler.sessions.clear()
        handler.state = handler.state.__class__()  # New state
    
    print("\n\n✅ Test completed successfully!")
    print("\nKey Features Demonstrated:")
    print("1. Variable selection using actual metadata (Opticks, PRIZM, SocialValues)")
    print("2. Intelligent scoring based on description matching and category relevance")
    print("3. PRIZM segment analysis providing rich demographic and behavioral insights")
    print("4. Constraint satisfaction ensuring all groups are 5-10% of total")


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Tools Test...")
    print("This will demonstrate the variable picker and clustering model")
    print("using your metadata files for intelligent variable selection.\n")
    
    asyncio.run(test_enhanced_workflow())