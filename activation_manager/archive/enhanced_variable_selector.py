"""
Enhanced Variable Selector Tool
Uses actual metadata files to intelligently select variables based on natural language
"""

import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Tuple
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from collections import defaultdict

# Add parent directory to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'Synthetic_Data'))
from metadata_loader import MetadataLoader


class EnhancedVariableSelector:
    """
    Advanced variable selector that uses real metadata to find relevant variables
    """
    
    def __init__(self, metadata_dir: str = "Synthetic_Data/Variable Metadata"):
        self.metadata_dir = metadata_dir
        self.variables_df = None
        self.category_mappings = {}
        self.keyword_index = defaultdict(list)
        self._load_all_metadata()
        
    def _load_metadata(self):
        """Alias for _load_all_metadata for backward compatibility"""
        return self._load_all_metadata()
    
    def _load_all_metadata(self):
        """Load and combine all metadata files into a unified dataframe"""
        all_variables = []
        
        # Load Opticks metadata
        opticks_df = self._load_opticks()
        if opticks_df is not None:
            all_variables.append(opticks_df)
            
        # Load Social Values metadata
        socialvalues_df = self._load_socialvalues()
        if socialvalues_df is not None:
            all_variables.append(socialvalues_df)
            
        # Load PRIZM metadata
        prizm_df = self._load_prizm()
        if prizm_df is not None:
            all_variables.append(prizm_df)
            
        # Combine all dataframes
        if all_variables:
            self.variables_df = pd.concat(all_variables, ignore_index=True)
            self._build_keyword_index()
            print(f"Loaded {len(self.variables_df)} variables total")
        else:
            print("Warning: No metadata loaded successfully")
            self.variables_df = pd.DataFrame()
        
        # Create variables list for backward compatibility
        self.variables = self.variables_df.to_dict('records') if not self.variables_df.empty else []
            
    def _load_opticks(self) -> pd.DataFrame:
        """Load Opticks metadata with proper structure"""
        try:
            filepath = os.path.join(self.metadata_dir, "opticks-powered-by-numeris---metadata.csv")
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Filter out geography variables
            df = df[~df['Variable'].isin(['CODE', 'GEO'])]
            
            # Standardize column names
            df['variable_code'] = df['Variable']
            df['description'] = df['Description']
            df['category'] = df['Category']
            df['source'] = 'opticks'
            
            # Map categories to our types
            df['variable_type'] = df['Category'].apply(self._map_category_to_type)
            
            return df[['variable_code', 'description', 'category', 'variable_type', 'source']]
            
        except Exception as e:
            print(f"Error loading Opticks metadata: {e}")
            return None
            
    def _load_socialvalues(self) -> pd.DataFrame:
        """Load Social Values metadata"""
        try:
            filepath = os.path.join(self.metadata_dir, "socialvalues-metadata.csv")
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Filter out geography variables
            df = df[~df['Variable'].isin(['CODE', 'GEO'])]
            
            # Standardize column names
            df['variable_code'] = df['Variable']
            df['description'] = df['Description']
            df['category'] = df.get('Category', 'Social Values')
            df['source'] = 'socialvalues'
            df['variable_type'] = 'psychographic'  # Social values are psychographic
            
            return df[['variable_code', 'description', 'category', 'variable_type', 'source']]
            
        except Exception as e:
            print(f"Error loading Social Values metadata: {e}")
            return None
            
    def _load_prizm(self) -> pd.DataFrame:
        """Load PRIZM metadata"""
        try:
            filepath = os.path.join(self.metadata_dir, "prizm-licences-metadata.csv")
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Filter out non-relevant variables
            exclude_vars = ['FSALDU', 'LATITUDE', 'LONGITUDE', 'COMMNAME']
            df = df[~df['Variable'].isin(exclude_vars)]
            
            # Standardize column names
            df['variable_code'] = df['Variable']
            df['description'] = df['Description']
            df['category'] = 'PRIZM Segments'
            df['source'] = 'prizm'
            df['variable_type'] = 'demographic'  # PRIZM segments are demographic
            
            return df[['variable_code', 'description', 'category', 'variable_type', 'source']]
            
        except Exception as e:
            print(f"Error loading PRIZM metadata: {e}")
            return None
            
    def _map_category_to_type(self, category: str) -> str:
        """Map metadata categories to our four types"""
        category_lower = str(category).lower()
        
        # Demographics
        if any(term in category_lower for term in ['basic', 'geography', 'age', 'gender', 'population', 'household']):
            return 'demographic'
            
        # Financial
        elif any(term in category_lower for term in ['financial', 'income', 'wealth', 'investment', 'credit', 'mortgage']):
            return 'financial'
            
        # Behavioral
        elif any(term in category_lower for term in ['product', 'service', 'consumption', 'purchase', 'usage', 
                                                     'automotive', 'retail', 'media', 'travel', 'health']):
            return 'behavioral'
            
        # Psychographic
        elif any(term in category_lower for term in ['values', 'lifestyle', 'attitude', 'opinion', 'interest']):
            return 'psychographic'
            
        # Default to behavioral for product/service categories
        else:
            return 'behavioral'
            
    def _build_keyword_index(self):
        """Build keyword index for fast searching"""
        if self.variables_df is None:
            return
            
        for idx, row in self.variables_df.iterrows():
            # Extract keywords from description
            description = str(row['description']).lower()
            words = re.findall(r'\b\w+\b', description)
            
            # Add to index
            for word in words:
                if len(word) > 2:  # Skip very short words
                    self.keyword_index[word].append(idx)
                    
            # Also index by category
            category_words = re.findall(r'\b\w+\b', str(row['category']).lower())
            for word in category_words:
                if len(word) > 2:
                    self.keyword_index[word].append(idx)
                    
    def analyze_request(self, user_request: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Analyze user request and return relevant variables
        
        Args:
            user_request: Natural language description of desired audience
            top_n: Number of top variables to return
            
        Returns:
            List of variable dictionaries with scores
        """
        if self.variables_df is None or len(self.variables_df) == 0:
            return []
            
        request_lower = user_request.lower()
        
        # Extract key terms and their importance
        term_weights = self._extract_weighted_terms(request_lower)
        
        # Score each variable
        variable_scores = []
        
        for idx, row in self.variables_df.iterrows():
            score = 0
            matched_terms = []
            
            # Score based on description match
            description_lower = str(row['description']).lower()
            for term, weight in term_weights.items():
                if term in description_lower:
                    score += weight * 2  # Higher weight for description matches
                    matched_terms.append(term)
                    
            # Score based on category match
            category_lower = str(row['category']).lower()
            for term, weight in term_weights.items():
                if term in category_lower:
                    score += weight
                    if term not in matched_terms:
                        matched_terms.append(term)
                        
            # Fuzzy matching for better results
            if score == 0:  # Try fuzzy matching if no exact matches
                desc_ratio = fuzz.partial_ratio(request_lower, description_lower)
                if desc_ratio > 70:
                    score = desc_ratio / 100.0
                    
            # Boost score based on variable type relevance
            type_boost = self._get_type_relevance_boost(request_lower, row['variable_type'])
            score *= (1 + type_boost)
            
            if score > 0:
                variable_scores.append({
                    'code': row['variable_code'],
                    'description': row['description'],
                    'category': row['category'],
                    'type': row['variable_type'],
                    'source': row['source'],
                    'score': round(score, 2),
                    'matched_terms': matched_terms[:3]  # Top 3 matched terms
                })
                
        # Sort by score and return top N
        variable_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Ensure diversity in results - mix different types
        diverse_results = self._ensure_diversity(variable_scores, top_n)
        
        return diverse_results
        
    def _extract_weighted_terms(self, text: str) -> Dict[str, float]:
        """Extract terms with importance weights"""
        # Important keywords get higher weights
        high_priority_terms = {
            # Demographics
            'millennial': 2.0, 'generation': 1.5, 'age': 1.5, 'young': 1.5, 'old': 1.5,
            'urban': 2.0, 'rural': 2.0, 'suburban': 2.0, 'city': 1.5, 'location': 1.5,
            'gender': 1.5, 'male': 1.5, 'female': 1.5, 'family': 2.0, 'children': 2.0,
            
            # Financial
            'income': 2.0, 'high income': 2.5, 'affluent': 2.5, 'wealthy': 2.5, 
            'disposable': 2.0, 'spending': 1.5, 'budget': 1.5, 'investment': 2.0,
            
            # Behavioral
            'purchase': 2.0, 'buy': 1.5, 'shop': 1.5, 'online': 2.0, 'frequent': 1.5,
            'travel': 2.0, 'automotive': 2.0, 'health': 2.0, 'media': 1.5,
            
            # Psychographic
            'conscious': 2.0, 'environmental': 2.5, 'green': 2.5, 'sustainable': 2.5,
            'values': 2.0, 'lifestyle': 2.0, 'interest': 1.5, 'opinion': 1.5,
            'tech': 2.0, 'technology': 2.0, 'innovation': 2.0, 'early adopter': 2.5
        }
        
        term_weights = {}
        
        # Check for high priority terms
        for term, weight in high_priority_terms.items():
            if term in text:
                term_weights[term] = weight
                
        # Extract other words with default weight
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 3 and word not in term_weights:
                term_weights[word] = 1.0
                
        return term_weights
        
    def _get_type_relevance_boost(self, request: str, var_type: str) -> float:
        """Get relevance boost based on variable type"""
        type_keywords = {
            'demographic': ['age', 'location', 'urban', 'rural', 'city', 'generation', 'millennial', 'family'],
            'financial': ['income', 'money', 'affluent', 'wealthy', 'disposable', 'spending', 'budget'],
            'behavioral': ['buy', 'purchase', 'shop', 'use', 'consume', 'travel', 'drive', 'online'],
            'psychographic': ['values', 'lifestyle', 'interest', 'conscious', 'opinion', 'belief', 'attitude']
        }
        
        boost = 0.0
        if var_type in type_keywords:
            for keyword in type_keywords[var_type]:
                if keyword in request:
                    boost += 0.2
                    
        return min(boost, 1.0)  # Cap at 100% boost
        
    def _ensure_diversity(self, variables: List[Dict], top_n: int) -> List[Dict]:
        """Ensure diverse mix of variable types in results"""
        # Group by type
        by_type = defaultdict(list)
        for var in variables:
            by_type[var['type']].append(var)
            
        # Take proportional amount from each type
        diverse_results = []
        per_type = max(3, top_n // 4)  # At least 3 per type if possible
        
        # First pass: take top variables from each type
        for var_type in ['demographic', 'behavioral', 'financial', 'psychographic']:
            if var_type in by_type:
                diverse_results.extend(by_type[var_type][:per_type])
                
        # Second pass: fill remaining slots with highest scoring variables
        if len(diverse_results) < top_n:
            remaining = top_n - len(diverse_results)
            all_remaining = [v for v in variables if v not in diverse_results]
            diverse_results.extend(all_remaining[:remaining])
            
        return diverse_results[:top_n]
        
    def get_variables_by_codes(self, codes: List[str]) -> pd.DataFrame:
        """Get full variable information by codes"""
        if self.variables_df is None:
            return pd.DataFrame()
            
        return self.variables_df[self.variables_df['variable_code'].isin(codes)]


# Test the enhanced selector
if __name__ == "__main__":
    selector = EnhancedVariableSelector()
    
    # Test queries
    test_queries = [
        "Find environmentally conscious millennials with high disposable income in urban areas",
        "Tech-savvy professionals who travel frequently",
        "Families with children interested in organic products",
        "Affluent retirees who invest in financial products"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        results = selector.analyze_request(query)
        
        for i, var in enumerate(results[:5], 1):
            print(f"{i}. {var['code']} - {var['description']}")
            print(f"   Type: {var['type']} | Category: {var['category']} | Score: {var['score']}")
            if var['matched_terms']:
                print(f"   Matched: {', '.join(var['matched_terms'])}")
            print()