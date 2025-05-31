#!/usr/bin/env python3
"""
Find demographic variables that might represent age and income
"""

import os
import sys
import re

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from activation_manager.core.enhanced_variable_selector_v3 import EnhancedVariableSelectorV3

def find_demographic_variables():
    """Find age and income related demographic variables"""
    
    print("🔍 Searching for Demographic Variables")
    print("=" * 80)
    
    # Initialize selector
    selector = EnhancedVariableSelectorV3(use_embeddings=True)
    
    # Categories to search
    categories = {
        'age_patterns': {
            'patterns': [
                r'\bage\b', r'\baged\b', r'\byears?\s+old\b', r'\b\d{2}-\d{2}\b',
                r'\b\d{2}\s+to\s+\d{2}\b', r'generation', r'birth', r'cohort'
            ],
            'variables': []
        },
        'income_patterns': {
            'patterns': [
                r'income', r'salary', r'earnings?', r'\$\d+', r'household.*income',
                r'hhi', r'wealth', r'net worth', r'financial'
            ],
            'variables': []
        },
        'prizm_segments': {
            'patterns': [
                r'prizm', r'segment', r'cluster', r'group\s+\d+', r'lifestyle'
            ],
            'variables': []
        }
    }
    
    # Search through all variables
    for idx, row in selector.variables_df.iterrows():
        desc_lower = str(row['description']).lower()
        code = str(row['code'])
        
        # Check each category
        for cat_name, cat_data in categories.items():
            for pattern in cat_data['patterns']:
                if re.search(pattern, desc_lower, re.IGNORECASE):
                    cat_data['variables'].append({
                        'code': code,
                        'description': row['description'],
                        'type': row.get('type', 'unknown'),
                        'source': row.get('source', 'unknown'),
                        'pattern': pattern
                    })
                    break
    
    # Display results
    for cat_name, cat_data in categories.items():
        print(f"\n📊 {cat_name.upper().replace('_', ' ')}:")
        print(f"Found {len(cat_data['variables'])} variables")
        print("-" * 60)
        
        # Deduplicate by code
        seen_codes = set()
        unique_vars = []
        for var in cat_data['variables']:
            if var['code'] not in seen_codes:
                seen_codes.add(var['code'])
                unique_vars.append(var)
        
        # Show examples
        for i, var in enumerate(unique_vars[:20], 1):
            print(f"{i}. {var['code']} [{var['type']}] - Pattern: {var['pattern']}")
            print(f"   {var['description'][:80]}...")
    
    # Look for PRIZM specific variables
    print("\n\n🎯 PRIZM SEGMENT ANALYSIS")
    print("=" * 80)
    
    prizm_vars = []
    for idx, row in selector.variables_df.iterrows():
        code = str(row['code'])
        desc = str(row['description'])
        
        # PRIZM codes often start with PR or contain PRIZM
        if code.startswith('PR') or 'PRIZM' in code.upper() or 'PRIZM' in desc.upper():
            prizm_vars.append({
                'code': code,
                'description': desc,
                'source': row.get('source', 'unknown')
            })
    
    print(f"\nFound {len(prizm_vars)} PRIZM variables")
    for i, var in enumerate(prizm_vars[:30], 1):
        print(f"{i}. {var['code']} - {var['description'][:70]}...")
    
    # Look for specific age codes
    print("\n\n📅 AGE-SPECIFIC CODES")
    print("=" * 80)
    
    age_codes = []
    age_keywords = ['AGE', 'YRS', 'YEAR', 'OLD', 'BIRTH', 'GEN']
    
    for idx, row in selector.variables_df.iterrows():
        code = str(row['code']).upper()
        
        if any(keyword in code for keyword in age_keywords):
            age_codes.append({
                'code': row['code'],
                'description': row['description'],
                'type': row.get('type', 'unknown')
            })
    
    print(f"\nFound {len(age_codes)} age-related codes")
    for i, var in enumerate(age_codes[:20], 1):
        print(f"{i}. {var['code']} [{var['type']}] - {var['description'][:60]}...")
    
    # Look for income codes
    print("\n\n💰 INCOME-SPECIFIC CODES")
    print("=" * 80)
    
    income_codes = []
    income_keywords = ['INC', 'HHI', 'SAL', 'EARN', 'WEALTH', '$']
    
    for idx, row in selector.variables_df.iterrows():
        code = str(row['code']).upper()
        desc = str(row['description']).upper()
        
        if any(keyword in code or keyword in desc for keyword in income_keywords):
            income_codes.append({
                'code': row['code'],
                'description': row['description'],
                'type': row.get('type', 'unknown')
            })
    
    print(f"\nFound {len(income_codes)} income-related codes")
    for i, var in enumerate(income_codes[:20], 1):
        print(f"{i}. {var['code']} [{var['type']}] - {var['description'][:60]}...")