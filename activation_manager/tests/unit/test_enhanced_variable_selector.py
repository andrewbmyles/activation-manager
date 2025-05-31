"""
Unit tests for VariableSelector
"""

import unittest
import tempfile
import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from enhanced_variable_selector import VariableSelector


class TestVariableSelector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.selector = VariableSelector()
        
        # Create test metadata files
        self.test_metadata_dir = tempfile.mkdtemp()
        
        # Test opticks metadata
        opticks_data = pd.DataFrame({
            'Variable Code': ['Q123', 'Q456', 'Q789'],
            'Description': ['Age of respondent', 'Income level high', 'Environmental consciousness'],
            'Category': ['Demographics', 'Financial', 'Lifestyle']
        })
        opticks_path = os.path.join(self.test_metadata_dir, 'opticks-powered-by-numeris---metadata.csv')
        opticks_data.to_csv(opticks_path, index=False)
        
        # Test PRIZM metadata
        prizm_data = pd.DataFrame({
            'code': ['PRIZM001', 'PRIZM002'],
            'description': ['Young urban professionals', 'Affluent suburban families'],
            'category': ['Demographic', 'Demographic']
        })
        prizm_path = os.path.join(self.test_metadata_dir, 'prizm-licences-metadata.csv')
        prizm_data.to_csv(prizm_path, index=False)
        
        # Test social values metadata  
        social_data = pd.DataFrame({
            'Code': ['SV001', 'SV002'],
            'Label': ['Technology adoption', 'Green lifestyle'],
            'Type': ['Behavioral', 'Psychographic']
        })
        social_path = os.path.join(self.test_metadata_dir, 'socialvalues-metadata.csv')
        social_data.to_csv(social_path, index=False)
        
        # Initialize selector with test data
        self.selector.metadata_dir = self.test_metadata_dir
        self.selector._load_metadata()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_metadata_dir)
    
    def test_metadata_loading(self):
        """Test that metadata files are loaded correctly"""
        self.assertGreater(len(self.selector.variables), 0)
        self.assertIn('keyword_index', dir(self.selector))
        
        # Check if variables from test files are loaded
        codes = [var['code'] for var in self.selector.variables]
        self.assertIn('Q123', codes)
        self.assertIn('PRIZM001', codes)
        self.assertIn('SV001', codes)
    
    def test_analyze_request_basic(self):
        """Test basic request analysis"""
        request = "Find young people with high income"
        results = self.selector.analyze_request(request, top_n=5)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
        
        if results:
            # Check result structure
            result = results[0]
            required_fields = ['code', 'description', 'type', 'score', 'source']
            for field in required_fields:
                self.assertIn(field, result)
            
            # Check score is positive
            self.assertGreater(result['score'], 0)
    
    def test_analyze_request_empty(self):
        """Test handling of empty request"""
        results = self.selector.analyze_request("", top_n=5)
        self.assertEqual(len(results), 0)
    
    def test_analyze_request_no_matches(self):
        """Test handling of request with no matches"""
        results = self.selector.analyze_request("xyzabc nonexistent term", top_n=5)
        self.assertEqual(len(results), 0)
    
    def test_keyword_matching(self):
        """Test keyword matching functionality"""
        # Test exact keyword match
        request = "income"
        results = self.selector.analyze_request(request, top_n=10)
        
        # Should find the income-related variable
        income_results = [r for r in results if 'income' in r['description'].lower()]
        self.assertGreater(len(income_results), 0)
    
    def test_fuzzy_matching(self):
        """Test fuzzy string matching"""
        # Test partial matches
        request = "enviornment"  # Misspelled
        results = self.selector.analyze_request(request, top_n=10)
        
        # Should still find environmental variables
        env_results = [r for r in results if 'environment' in r['description'].lower()]
        self.assertGreater(len(env_results), 0)
    
    def test_category_scoring(self):
        """Test category-based scoring"""
        request = "demographic information"
        results = self.selector.analyze_request(request, top_n=10)
        
        # Demographic variables should score higher
        if results:
            for result in results[:3]:  # Top 3 should be relevant
                self.assertIn(result['type'].lower(), ['demographic', 'demographics'])
    
    def test_diversity_enforcement(self):
        """Test that results include diverse variable types"""
        request = "target audience with lifestyle and income"
        results = self.selector.analyze_request(request, top_n=10)
        
        if len(results) >= 4:
            types = [r['type'] for r in results]
            unique_types = set(types)
            # Should have some diversity in types
            self.assertGreaterEqual(len(unique_types), 2)
    
    def test_top_n_limit(self):
        """Test that top_n parameter is respected"""
        request = "any variables"
        results = self.selector.analyze_request(request, top_n=3)
        self.assertLessEqual(len(results), 3)
    
    def test_score_ordering(self):
        """Test that results are ordered by score (descending)"""
        request = "income and age"
        results = self.selector.analyze_request(request, top_n=5)
        
        if len(results) > 1:
            scores = [r['score'] for r in results]
            self.assertEqual(scores, sorted(scores, reverse=True))


class TestVariableSelectorIntegration(unittest.TestCase):
    """Integration tests with real metadata files"""
    
    def setUp(self):
        """Set up with real metadata directory"""
        self.selector = VariableSelector()
        
        # Check if real metadata exists
        metadata_dir = "/Users/myles/Documents/Activation Manager/Synthetic_Data/Variable Metadata"
        if os.path.exists(metadata_dir):
            self.selector.metadata_dir = metadata_dir
            self.selector._load_metadata()
            self.has_real_data = True
        else:
            self.has_real_data = False
    
    def test_real_metadata_loading(self):
        """Test loading real metadata files"""
        if not self.has_real_data:
            self.skipTest("Real metadata files not available")
        
        self.assertGreater(len(self.selector.variables), 100)  # Should have many variables
        
        # Check data structure
        variable = self.selector.variables[0]
        required_fields = ['code', 'description', 'type', 'source']
        for field in required_fields:
            self.assertIn(field, variable)
    
    def test_realistic_queries(self):
        """Test with realistic audience queries"""
        if not self.has_real_data:
            self.skipTest("Real metadata files not available")
        
        test_queries = [
            "environmentally conscious millennials with high income",
            "tech-savvy families with children",
            "affluent seniors interested in travel",
            "urban professionals who shop online"
        ]
        
        for query in test_queries:
            with self.subTest(query=query):
                results = self.selector.analyze_request(query, top_n=15)
                
                self.assertGreater(len(results), 0, f"No results for query: {query}")
                self.assertLessEqual(len(results), 15)
                
                # Check result quality
                top_result = results[0]
                self.assertGreater(top_result['score'], 0)
                self.assertIsInstance(top_result['description'], str)
                self.assertGreater(len(top_result['description']), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)