"""
Unit tests for PRIZMAnalyzer
"""

import unittest
import pandas as pd
import numpy as np
from prizm_analyzer import PRIZMAnalyzer


class TestPRIZMAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = PRIZMAnalyzer()
        
        # Create test data with PRIZM segments
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'Group': [0, 0, 0, 1, 1, 1, 2, 2, 2],
            'PRIZM_CLUSTER': [
                'Young Digerati', 'Young Digerati', 'Money & Brains',
                'Kids & Cul-de-Sacs', 'Kids & Cul-de-Sacs', 'Pools & Patios',
                'Golden Ponds', 'Golden Ponds', 'Heartlanders'
            ],
            'AGE_RANGE': ['25-34', '25-34', '35-44', '35-44', '35-44', '45-54', '55-64', '65+', '55-64'],
            'INCOME_LEVEL': ['High', 'High', 'High', 'Medium', 'Medium', 'High', 'Medium', 'Medium', 'Low']
        })
    
    def test_segment_profiles_exist(self):
        """Test that PRIZM segment profiles are loaded"""
        self.assertGreater(len(self.analyzer.segment_profiles), 0)
        
        # Check structure of a sample profile
        sample_key = list(self.analyzer.segment_profiles.keys())[0]
        sample_profile = self.analyzer.segment_profiles[sample_key]
        
        required_fields = ['description', 'demographics', 'behaviors', 'psychographics']
        for field in required_fields:
            self.assertIn(field, sample_profile)
    
    def test_analyze_segment_distribution_basic(self):
        """Test basic segment distribution analysis"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        
        # Check overall structure
        self.assertIn('segment_profiles', result)
        self.assertIn('overall_summary', result)
        
        # Check that we have profiles for each group
        expected_groups = ['0', '1', '2']
        for group in expected_groups:
            self.assertIn(group, result['segment_profiles'])
    
    def test_segment_profile_structure(self):
        """Test structure of individual segment profiles"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        
        # Check first segment profile
        group_0_profile = result['segment_profiles']['0']
        
        required_fields = [
            'dominant_segments', 'demographics', 'key_behaviors', 
            'psychographics', 'marketing_implications'
        ]
        
        for field in required_fields:
            self.assertIn(field, group_0_profile)
        
        # Check data types
        self.assertIsInstance(group_0_profile['dominant_segments'], list)
        self.assertIsInstance(group_0_profile['demographics'], str)
        self.assertIsInstance(group_0_profile['key_behaviors'], list)
    
    def test_dominant_segment_calculation(self):
        """Test that dominant segments are calculated correctly"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        
        # Group 0 should have Young Digerati as dominant (2 out of 3)
        group_0_segments = result['segment_profiles']['0']['dominant_segments']
        self.assertIn('Young Digerati', group_0_segments[0])
    
    def test_overall_summary(self):
        """Test overall summary generation"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        summary = result['overall_summary']
        
        required_fields = [
            'total_segments', 'diversity_score', 'top_segments', 'market_potential_index'
        ]
        
        for field in required_fields:
            self.assertIn(field, summary)
        
        # Check data types and ranges
        self.assertIsInstance(summary['total_segments'], int)
        self.assertGreaterEqual(summary['diversity_score'], 0)
        self.assertLessEqual(summary['diversity_score'], 1)
        self.assertIsInstance(summary['top_segments'], list)
    
    def test_diversity_score_calculation(self):
        """Test diversity score calculation"""
        # Create uniform data (low diversity)
        uniform_data = pd.DataFrame({
            'Group': [0, 0, 0, 1, 1, 1],
            'PRIZM_CLUSTER': ['Young Digerati'] * 6
        })
        
        # Create diverse data
        diverse_data = pd.DataFrame({
            'Group': [0, 0, 0, 1, 1, 1],
            'PRIZM_CLUSTER': ['Young Digerati', 'Money & Brains', 'Kids & Cul-de-Sacs', 
                             'Pools & Patios', 'Golden Ponds', 'Heartlanders']
        })
        
        uniform_result = self.analyzer.analyze_segment_distribution(uniform_data)
        diverse_result = self.analyzer.analyze_segment_distribution(diverse_data)
        
        uniform_diversity = uniform_result['overall_summary']['diversity_score']
        diverse_diversity = diverse_result['overall_summary']['diversity_score']
        
        # Diverse data should have higher diversity score
        self.assertGreater(diverse_diversity, uniform_diversity)
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = pd.DataFrame(columns=['Group', 'PRIZM_CLUSTER'])
        
        result = self.analyzer.analyze_segment_distribution(empty_data)
        
        self.assertIn('segment_profiles', result)
        self.assertIn('overall_summary', result)
        self.assertEqual(len(result['segment_profiles']), 0)
    
    def test_missing_prizm_column(self):
        """Test handling of data without PRIZM_CLUSTER column"""
        data_without_prizm = pd.DataFrame({
            'Group': [0, 1, 2],
            'AGE_RANGE': ['25-34', '35-44', '45-54']
        })
        
        result = self.analyzer.analyze_segment_distribution(data_without_prizm)
        
        # Should still return structure but with limited analysis
        self.assertIn('segment_profiles', result)
        self.assertIn('overall_summary', result)
    
    def test_marketing_implications_generation(self):
        """Test that marketing implications are generated"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        
        for group_id, profile in result['segment_profiles'].items():
            implications = profile['marketing_implications']
            
            self.assertIsInstance(implications, str)
            self.assertGreater(len(implications), 10)  # Should be substantive
    
    def test_segment_profile_lookup(self):
        """Test that segment profiles are correctly looked up"""
        # Test known segment
        profile = self.analyzer._get_segment_profile('Young Digerati')
        
        self.assertIsInstance(profile, dict)
        self.assertIn('description', profile)
        self.assertIn('demographics', profile)
        
        # Test unknown segment
        unknown_profile = self.analyzer._get_segment_profile('Unknown Segment')
        self.assertIsInstance(unknown_profile, dict)
        self.assertIn('description', unknown_profile)
    
    def test_market_potential_calculation(self):
        """Test market potential index calculation"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        market_potential = result['overall_summary']['market_potential_index']
        
        # Should be a number between 0 and 10
        self.assertIsInstance(market_potential, (int, float))
        self.assertGreaterEqual(market_potential, 0)
        self.assertLessEqual(market_potential, 10)
    
    def test_behavioral_extraction(self):
        """Test extraction of key behaviors"""
        result = self.analyzer.analyze_segment_distribution(self.test_data)
        
        for group_id, profile in result['segment_profiles'].items():
            behaviors = profile['key_behaviors']
            
            self.assertIsInstance(behaviors, list)
            if behaviors:  # If there are behaviors
                for behavior in behaviors:
                    self.assertIsInstance(behavior, str)
                    self.assertGreater(len(behavior), 0)


class TestPRIZMAnalyzerPerformance(unittest.TestCase):
    """Performance and scalability tests"""
    
    def setUp(self):
        self.analyzer = PRIZMAnalyzer()
    
    def test_large_dataset_performance(self):
        """Test performance with larger dataset"""
        # Create larger test dataset
        np.random.seed(42)
        n_rows = 10000
        
        prizm_segments = ['Young Digerati', 'Money & Brains', 'Kids & Cul-de-Sacs', 
                         'Pools & Patios', 'Golden Ponds', 'Heartlanders']
        
        large_data = pd.DataFrame({
            'Group': np.random.randint(0, 10, n_rows),
            'PRIZM_CLUSTER': np.random.choice(prizm_segments, n_rows)
        })
        
        import time
        start_time = time.time()
        result = self.analyzer.analyze_segment_distribution(large_data)
        end_time = time.time()
        
        # Should complete within reasonable time (< 5 seconds)
        self.assertLess(end_time - start_time, 5.0)
        
        # Should still produce valid results
        self.assertIn('segment_profiles', result)
        self.assertIn('overall_summary', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)