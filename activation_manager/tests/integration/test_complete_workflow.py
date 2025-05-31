"""
Integration tests for complete enhanced search workflow
Tests the full pipeline from data loading to search results
"""

import unittest
import os
import json
import time
from pathlib import Path

# Only run if we have the actual data files
SKIP_INTEGRATION = not Path("/Users/myles/Documents/Activation Manager/data/variables_2022_can.parquet").exists()


@unittest.skipIf(SKIP_INTEGRATION, "Skipping integration tests - data files not available")
class TestCompleteWorkflow(unittest.TestCase):
    """Integration tests for the complete enhanced search workflow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up once for all tests"""
        from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI
        
        # Initialize API without OpenAI key for testing
        cls.api = EnhancedVariablePickerAPI(openai_api_key=os.getenv('OPENAI_API_KEY'))
        
        # Get stats to verify loading
        cls.stats = cls.api.get_variable_stats()
    
    def test_data_loading(self):
        """Test that data loads correctly"""
        # Should have loaded all variables
        self.assertEqual(self.stats['total_variables'], 49323)
        
        # Should have all themes
        self.assertEqual(len(self.stats['themes']), 5)
        self.assertIn('Behavioural', self.stats['themes'])
        self.assertIn('Demographic', self.stats['themes'])
        self.assertIn('Financial', self.stats['themes'])
        
        # Should have multiple products
        self.assertGreater(len(self.stats['products']), 20)
    
    def test_basic_search(self):
        """Test basic search functionality"""
        # Test simple query
        results = self.api.search_variables('household income', top_k=10)
        
        self.assertIn('results', results)
        self.assertGreater(len(results['results']), 0)
        self.assertLessEqual(len(results['results']), 10)
        
        # Check result structure
        first_result = results['results'][0]
        self.assertIn('code', first_result)
        self.assertIn('description', first_result)
        self.assertIn('score', first_result)
    
    def test_50_result_search(self):
        """Test that we can get 50 results"""
        # Search for a broad term
        results = self.api.search_variables('age', top_k=50)
        
        self.assertEqual(len(results['results']), 50)
        
        # Verify results are sorted by score
        scores = [r['score'] for r in results['results']]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_domain_specific_searches(self):
        """Test searches for each domain"""
        domain_queries = {
            'automotive': 'luxury vehicles',
            'demographic': 'millennials age 25-34',
            'financial': 'high income over 150k',
            'health': 'disability and wellness',
            'immigration': 'new immigrants permanent residents'
        }
        
        for domain, query in domain_queries.items():
            results = self.api.search_variables(query, top_k=20)
            
            self.assertGreater(len(results['results']), 0, 
                             f"No results for {domain} query: {query}")
            
            # Check that results are relevant (contain query terms)
            relevant_count = 0
            for result in results['results'][:10]:
                desc_lower = result.get('description', '').lower()
                if any(term in desc_lower for term in query.lower().split()):
                    relevant_count += 1
            
            self.assertGreater(relevant_count, 5, 
                             f"Few relevant results for {domain}")
    
    def test_numeric_pattern_search(self):
        """Test numeric pattern recognition"""
        numeric_queries = [
            'age 18 to 24',
            'income between 50k and 100k',
            'over 65 years',
            'top 10 percent'
        ]
        
        for query in numeric_queries:
            results = self.api.search_variables(query, top_k=10)
            
            self.assertGreater(len(results['results']), 0,
                             f"No results for numeric query: {query}")
            
            # Query context should have numeric components
            if 'query_context' in results:
                context = results['query_context']
                if 'numeric_components' in context:
                    self.assertTrue(len(context['numeric_components']) > 0,
                                  f"No numeric patterns found in: {query}")
    
    def test_category_search(self):
        """Test category-based search"""
        # Test some known categories
        categories = ['Income', 'Age', 'Vehicle']
        
        for category in categories:
            results = self.api.search_by_category(category, top_k=20)
            
            self.assertGreater(len(results), 0,
                             f"No results for category: {category}")
            
            # All results should have the category
            for var in results[:5]:
                self.assertIn(category.lower(), var.get('category', '').lower())
    
    def test_variable_lookup(self):
        """Test direct variable lookup"""
        # Get a variable from search results
        search_results = self.api.search_variables('total households', top_k=5)
        
        if search_results['results']:
            var_id = search_results['results'][0]['code']
            
            # Look up the variable directly
            var = self.api.get_variable_by_id(var_id)
            
            self.assertIsNotNone(var)
            self.assertEqual(var['code'], var_id)
    
    def test_search_performance(self):
        """Test search performance"""
        queries = [
            'household income',
            'vehicle ownership',
            'age demographics',
            'health spending',
            'immigration status'
        ]
        
        # Warm up
        self.api.search_variables('test', top_k=10)
        
        # Time searches
        total_time = 0
        for query in queries:
            start = time.time()
            results = self.api.search_variables(query, top_k=50)
            elapsed = time.time() - start
            total_time += elapsed
            
            # Each search should be reasonably fast
            self.assertLess(elapsed, 2.0, 
                          f"Search too slow for '{query}': {elapsed:.2f}s")
        
        avg_time = total_time / len(queries)
        self.assertLess(avg_time, 1.0,
                       f"Average search time too high: {avg_time:.2f}s")
    
    def test_mixed_search_methods(self):
        """Test combining keyword and semantic search"""
        # Test keyword only
        keyword_results = self.api.search_variables(
            'VIOPCAR', 
            top_k=10, 
            use_semantic=False
        )
        
        # Test semantic only (if available)
        if self.api.enhanced_search and hasattr(self.api.enhanced_search, 'openai_client'):
            semantic_results = self.api.search_variables(
                'passenger vehicles',
                top_k=10,
                use_keyword=False
            )
            
            # Both should return results
            self.assertGreater(len(keyword_results['results']), 0)
            self.assertGreater(len(semantic_results['results']), 0)
    
    def test_result_grouping(self):
        """Test result grouping functionality"""
        results = self.api.search_variables('income age vehicle', top_k=50)
        
        if 'grouped' in results and results['grouped']:
            grouped = results['grouped']
            
            # Should have groupings
            if 'by_theme' in grouped:
                themes = grouped['by_theme']
                self.assertGreater(len(themes), 0)
                
                # Each theme should have variables
                for theme, vars in themes.items():
                    self.assertIsInstance(vars, list)
                    self.assertGreater(len(vars), 0)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty query
        results = self.api.search_variables('', top_k=10)
        self.assertEqual(len(results['results']), 0)
        
        # Very long query
        long_query = ' '.join(['test'] * 50)
        results = self.api.search_variables(long_query, top_k=10)
        self.assertIsInstance(results['results'], list)
        
        # Special characters
        results = self.api.search_variables('test!@#$%', top_k=10)
        self.assertIsInstance(results['results'], list)
        
        # Non-existent category
        results = self.api.search_by_category('NonExistentCategory')
        self.assertEqual(len(results), 0)
        
        # Non-existent variable ID
        var = self.api.get_variable_by_id('DOESNOTEXIST')
        self.assertIsNone(var)


if __name__ == '__main__':
    if SKIP_INTEGRATION:
        print("⚠️  Integration tests skipped - data files not available")
        print("   To run integration tests, ensure parquet file exists at:")
        print("   /Users/myles/Documents/Activation Manager/data/variables_2022_can.parquet")
    else:
        unittest.main()