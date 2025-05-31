#!/usr/bin/env python3
"""
Test script to demonstrate improved variable picker effectiveness
Compares original results vs enhanced V2 results
"""

import sys
import os
from enhanced_variable_selector import EnhancedVariableSelector
from enhanced_variable_selector_v2 import EnhancedVariableSelectorV2

def test_variable_picker_improvements():
    """Test and compare variable picker results before and after improvements"""
    
    # Test query that was problematic
    test_query = "environmentally conscious millennials with high disposable income who live in urban areas"
    
    print("🔍 Variable Picker Effectiveness Test")
    print("="*60)
    print(f"Query: '{test_query}'")
    print("="*60)
    
    try:
        # Test original selector
        print("\n📊 ORIGINAL VARIABLE SELECTOR RESULTS:")
        print("-" * 40)
        
        original_selector = EnhancedVariableSelector()
        original_results = original_selector.analyze_request(test_query, top_n=10)
        
        print(f"Found {len(original_results)} variables:")
        for i, var in enumerate(original_results, 1):
            print(f"{i:2d}. {var['code']:25} | {var['description'][:50]:50} | Score: {var['score']:5.2f}")
        
        # Analyze issues with original results
        print(f"\n🔍 ANALYSIS OF ORIGINAL RESULTS:")
        print("-" * 40)
        
        age_vars = [v for v in original_results if any(term in v['description'].lower() 
                   for term in ['age', 'millennial', 'young', 'generation'])]
        income_vars = [v for v in original_results if any(term in v['description'].lower() 
                      for term in ['income', 'disposable', 'affluent', 'earning'])]
        env_vars = [v for v in original_results if any(term in v['description'].lower() 
                   for term in ['environment', 'green', 'sustainable', 'eco'])]
        location_vars = [v for v in original_results if any(term in v['description'].lower() 
                        for term in ['urban', 'city', 'location', 'geography'])]
        
        print(f"  Age/Millennial variables: {len(age_vars)}")
        print(f"  Income variables: {len(income_vars)}")
        print(f"  Environmental variables: {len(env_vars)}")
        print(f"  Urban/Location variables: {len(location_vars)}")
        
        if len(age_vars) == 0:
            print("  ❌ Missing age/millennial variables despite query mentioning 'millennials'")
        if len(income_vars) == 0:
            print("  ❌ Missing income variables despite query mentioning 'high disposable income'")
        if len(env_vars) == 0:
            print("  ❌ Missing environmental variables despite query mentioning 'environmentally conscious'")
        if len(location_vars) == 0:
            print("  ❌ Missing location variables despite query mentioning 'urban areas'")
            
    except Exception as e:
        print(f"❌ Error with original selector: {e}")
        original_results = []
    
    try:
        # Test enhanced V2 selector
        print(f"\n🚀 ENHANCED V2 VARIABLE SELECTOR RESULTS:")
        print("-" * 40)
        
        enhanced_selector = EnhancedVariableSelectorV2()
        enhanced_results = enhanced_selector.analyze_request(test_query, top_n=10)
        
        print(f"Found {len(enhanced_results)} variables:")
        for i, var in enumerate(enhanced_results, 1):
            print(f"{i:2d}. {var['code']:25} | {var['description'][:50]:50} | Score: {var['score']:5.2f}")
        
        # Analyze improvements in enhanced results
        print(f"\n✅ ANALYSIS OF ENHANCED RESULTS:")
        print("-" * 40)
        
        age_vars_v2 = [v for v in enhanced_results if any(term in v['description'].lower() 
                      for term in ['age', 'millennial', 'young', 'generation'])]
        income_vars_v2 = [v for v in enhanced_results if any(term in v['description'].lower() 
                         for term in ['income', 'disposable', 'affluent', 'earning'])]
        env_vars_v2 = [v for v in enhanced_results if any(term in v['description'].lower() 
                      for term in ['environment', 'green', 'sustainable', 'eco'])]
        location_vars_v2 = [v for v in enhanced_results if any(term in v['description'].lower() 
                           for term in ['urban', 'city', 'location', 'geography'])]
        
        print(f"  Age/Millennial variables: {len(age_vars_v2)}")
        print(f"  Income variables: {len(income_vars_v2)}")
        print(f"  Environmental variables: {len(env_vars_v2)}")
        print(f"  Urban/Location variables: {len(location_vars_v2)}")
        
        # Show specific improvements
        improvements = []
        if len(age_vars_v2) > len(age_vars):
            improvements.append(f"✅ Added {len(age_vars_v2) - len(age_vars)} age/millennial variables")
        if len(income_vars_v2) > len(income_vars):
            improvements.append(f"✅ Added {len(income_vars_v2) - len(income_vars)} income variables")
        if len(env_vars_v2) > len(env_vars):
            improvements.append(f"✅ Added {len(env_vars_v2) - len(env_vars)} environmental variables")
        if len(location_vars_v2) > len(location_vars):
            improvements.append(f"✅ Added {len(location_vars_v2) - len(location_vars)} location variables")
        
        if improvements:
            print("\n🎯 KEY IMPROVEMENTS:")
            for improvement in improvements:
                print(f"  {improvement}")
        
        # Check for better semantic matching
        total_score_v2 = sum(var['score'] for var in enhanced_results)
        if len(original_results) > 0:
            total_score_orig = sum(var['score'] for var in original_results)
            if total_score_v2 > total_score_orig:
                print(f"  ✅ Higher overall relevance scores ({total_score_v2:.2f} vs {total_score_orig:.2f})")
        
        # Show variable type diversity
        types_v2 = set(var['type'] for var in enhanced_results)
        print(f"  ✅ Variable type diversity: {len(types_v2)} types ({', '.join(sorted(types_v2))})")
        
    except Exception as e:
        print(f"❌ Error with enhanced selector: {e}")
        enhanced_results = []
    
    # Summary comparison
    print(f"\n📈 EFFECTIVENESS SUMMARY:")
    print("="*60)
    
    if len(original_results) > 0 and len(enhanced_results) > 0:
        print(f"Original selector: {len(original_results)} variables")
        print(f"Enhanced V2 selector: {len(enhanced_results)} variables")
        
        # Count relevant variables for the query
        orig_relevant = len([v for v in original_results if any(
            term in v['description'].lower() 
            for term in ['age', 'millennial', 'income', 'disposable', 'environment', 'green', 'urban', 'city']
        )])
        
        v2_relevant = len([v for v in enhanced_results if any(
            term in v['description'].lower() 
            for term in ['age', 'millennial', 'income', 'disposable', 'environment', 'green', 'urban', 'city']
        )])
        
        print(f"Relevant variables - Original: {orig_relevant}/{len(original_results)} ({orig_relevant/len(original_results)*100:.1f}%)")
        print(f"Relevant variables - Enhanced: {v2_relevant}/{len(enhanced_results)} ({v2_relevant/len(enhanced_results)*100:.1f}%)")
        
        if v2_relevant > orig_relevant:
            print(f"🎉 Enhanced selector found {v2_relevant - orig_relevant} more relevant variables!")
        
        # Show average scores
        avg_score_orig = sum(var['score'] for var in original_results) / len(original_results)
        avg_score_v2 = sum(var['score'] for var in enhanced_results) / len(enhanced_results)
        
        print(f"Average relevance score - Original: {avg_score_orig:.2f}")
        print(f"Average relevance score - Enhanced: {avg_score_v2:.2f}")
        
        if avg_score_v2 > avg_score_orig:
            improvement_pct = ((avg_score_v2 - avg_score_orig) / avg_score_orig) * 100
            print(f"🚀 {improvement_pct:.1f}% improvement in average relevance scores!")
    
    return enhanced_results

def test_additional_queries():
    """Test the enhanced selector with additional challenging queries"""
    
    print(f"\n🎯 ADDITIONAL QUERY TESTS:")
    print("="*60)
    
    test_queries = [
        "tech-savvy young professionals in major cities",
        "budget-conscious families with children",
        "affluent retirees interested in luxury travel",
        "health-conscious women aged 25-40"
    ]
    
    try:
        enhanced_selector = EnhancedVariableSelectorV2()
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 50)
            
            results = enhanced_selector.analyze_request(query, top_n=5)
            
            for j, var in enumerate(results, 1):
                print(f"   {j}. {var['code']:20} | {var['description'][:35]:35} | {var['score']:5.2f}")
                
    except Exception as e:
        print(f"❌ Error testing additional queries: {e}")

if __name__ == "__main__":
    print("Starting Variable Picker Effectiveness Test...")
    print()
    
    # Run main comparison test
    enhanced_results = test_variable_picker_improvements()
    
    # Run additional tests
    test_additional_queries()
    
    print(f"\n✅ Test complete! Enhanced variable selector V2 is now integrated.")
    print("The improved selector should show better relevance matching for audience queries.")