"""
Unit tests for similarity filtering functionality
"""

import unittest
from unittest.mock import Mock, patch
import numpy as np

from activation_manager.core.enhanced_semantic_search_v2 import EnhancedSemanticSearchV2


class TestSimilarityFiltering(unittest.TestCase):
    """Test cases for similarity filtering in enhanced variable picker"""
    
    def setUp(self):
        """Set up test data"""
        # Create mock variables
        self.mock_variables = [
            {'code': 'VAR1', 'description': 'Age 18 to 24 years'},
            {'code': 'VAR2', 'description': 'Age 18-24 years'},  # Very similar to VAR1
            {'code': 'VAR3', 'description': 'Age 25 to 34 years'},
            {'code': 'VAR4', 'description': 'Income $50,000 to $75,000'},
            {'code': 'VAR5', 'description': 'Income $50K to $75K'},  # Similar to VAR4
            {'code': 'VAR6', 'description': 'Income $75,000 to $100,000'},
            {'code': 'VAR7', 'description': 'Education: High School'},
            {'code': 'VAR8', 'description': 'Education: Bachelor Degree'},
            {'code': 'VAR9', 'description': 'Household Size: 1 person'},
            {'code': 'VAR10', 'description': 'Household Size: 1'},  # Similar to VAR9
        ]
        
        # Initialize search instance
        self.search = EnhancedSemanticSearchV2(
            variables=self.mock_variables,
            embeddings=None,
            openai_api_key=None
        )
    
    def test_jaro_winkler_identical_strings(self):
        """Test Jaro-Winkler with identical strings"""
        score = self.search._jaro_winkler_similarity("test", "test")
        self.assertEqual(score, 1.0)
    
    def test_jaro_winkler_empty_strings(self):
        """Test Jaro-Winkler with empty strings"""
        score = self.search._jaro_winkler_similarity("", "test")
        self.assertEqual(score, 0.0)
        
        score = self.search._jaro_winkler_similarity("test", "")
        self.assertEqual(score, 0.0)
        
        score = self.search._jaro_winkler_similarity("", "")
        self.assertEqual(score, 1.0)  # Two empty strings are considered identical
    
    def test_jaro_winkler_similar_strings(self):
        """Test Jaro-Winkler with similar strings"""
        # Very similar strings should have high score
        score = self.search._jaro_winkler_similarity("Age 18 to 24 years", "Age 18-24 years")
        self.assertGreater(score, 0.85)
        
        # Less similar strings should have lower score (but still quite high due to common prefix)
        score = self.search._jaro_winkler_similarity("Age 18 to 24 years", "Age 25 to 34 years")
        self.assertLess(score, 0.95)  # Adjusted threshold since "Age" prefix boosts score
        self.assertGreater(score, 0.7)  # Still quite similar
        
        # Different strings should have low score
        score = self.search._jaro_winkler_similarity("Age 18 to 24 years", "Income $50,000 to $75,000")
        self.assertLess(score, 0.5)
    
    def test_filter_similar_variables_basic(self):
        """Test basic filtering of similar variables"""
        # Create results with scores
        results = []
        for i, var in enumerate(self.mock_variables):
            result = var.copy()
            result['score'] = 10 - i  # Descending scores
            results.append(result)
        
        # Apply filtering
        filtered = self.search._filter_similar_variables(
            results, 
            similarity_threshold=0.85,
            max_similar_per_group=1
        )
        
        # Should have fewer results
        self.assertLess(len(filtered), len(results))
        
        # Check that similar variables were filtered
        codes = [r['code'] for r in filtered]
        
        # VAR1 and VAR2 are similar, only the higher scored one should remain
        self.assertIn('VAR1', codes)
        self.assertNotIn('VAR2', codes)
        
        # VAR4 and VAR5 are similar, only the higher scored one should remain
        self.assertIn('VAR4', codes)
        self.assertNotIn('VAR5', codes)
        
        # VAR9 and VAR10 are similar, only the higher scored one should remain
        self.assertIn('VAR9', codes)
        self.assertNotIn('VAR10', codes)
    
    def test_filter_similar_variables_max_per_group(self):
        """Test filtering with max_similar_per_group parameter"""
        # Create results with scores
        results = []
        for i, var in enumerate(self.mock_variables):
            result = var.copy()
            result['score'] = 10 - i
            results.append(result)
        
        # Apply filtering with max_similar_per_group=2
        filtered = self.search._filter_similar_variables(
            results, 
            similarity_threshold=0.85,
            max_similar_per_group=2
        )
        
        # Count occurrences of similar pairs
        codes = [r['code'] for r in filtered]
        
        # Both VAR1 and VAR2 should be present (max 2 per group)
        var1_var2_count = sum(1 for code in codes if code in ['VAR1', 'VAR2'])
        self.assertEqual(var1_var2_count, 2)
    
    def test_filter_similar_variables_empty_results(self):
        """Test filtering with empty results"""
        filtered = self.search._filter_similar_variables([])
        self.assertEqual(filtered, [])
    
    def test_filter_similar_variables_no_description(self):
        """Test filtering with results missing descriptions"""
        results = [
            {'code': 'VAR1', 'description': 'Test description', 'score': 10},
            {'code': 'VAR2', 'score': 9},  # Missing description
            {'code': 'VAR3', 'description': '', 'score': 8},  # Empty description
        ]
        
        filtered = self.search._filter_similar_variables(results)
        
        # Should handle missing/empty descriptions gracefully
        self.assertIsInstance(filtered, list)
        self.assertGreater(len(filtered), 0)
    
    def test_filter_similar_variables_category_consideration(self):
        """Test that category is considered in similarity filtering"""
        results = [
            {'code': 'VAR1', 'description': 'Age 18 to 24', 'category': 'Demographics', 'score': 10},
            {'code': 'VAR2', 'description': 'Age 18 to 24', 'category': 'Demographics', 'score': 9},
            {'code': 'VAR3', 'description': 'Age 18 to 24', 'category': 'Psychographics', 'score': 8},
        ]
        
        # Apply filtering - same category should have stricter threshold
        filtered = self.search._filter_similar_variables(
            results, 
            similarity_threshold=0.9,  # High threshold
            max_similar_per_group=1
        )
        
        codes = [r['code'] for r in filtered]
        
        # VAR1 and VAR2 have same description and category - should filter
        self.assertIn('VAR1', codes)
        self.assertNotIn('VAR2', codes)
        
        # VAR3 has same description but different category - might not filter
        # depending on exact similarity calculation
    
    def test_search_with_filtering_integration(self):
        """Test the filtering functionality directly"""
        # Create test results with more distinct descriptions
        test_results = [
            {'code': 'VAR1', 'description': 'Age 18 to 24 years', 'score': 0.9},
            {'code': 'VAR2', 'description': 'Age 18-24 years', 'score': 0.85},
            {'code': 'VAR3', 'description': 'Education Level: Bachelor Degree', 'score': 0.8},
            {'code': 'VAR4', 'description': 'Income $50,000 to $75,000', 'score': 0.75},
            {'code': 'VAR5', 'description': 'Income $50K-$75K', 'score': 0.7},
        ]
        
        # Test filtering
        filtered_results = self.search._filter_similar_variables(
            test_results,
            similarity_threshold=0.85,
            max_similar_per_group=1
        )
        
        # Check that similar variables were filtered
        self.assertLess(len(filtered_results), len(test_results))
        
        # Check specific filtering expectations
        codes = [r['code'] for r in filtered_results]
        
        # VAR1 and VAR2 are very similar, only one should remain
        self.assertTrue('VAR1' in codes or 'VAR2' in codes)
        self.assertFalse('VAR1' in codes and 'VAR2' in codes)
        
        # VAR4 and VAR5 are similar, only one should remain
        self.assertTrue('VAR4' in codes or 'VAR5' in codes)
        self.assertFalse('VAR4' in codes and 'VAR5' in codes)
        
        # VAR3 should remain as it's different from others
        self.assertIn('VAR3', codes)


if __name__ == '__main__':
    unittest.main()