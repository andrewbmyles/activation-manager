"""
Unit tests for ConstrainedKMedians clustering
"""

import unittest
import pandas as pd
import numpy as np
from audience_builder import ConstrainedKMedians


class TestConstrainedKMedians(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        np.random.seed(42)
        
        # Create test dataset with mixed data types
        self.test_data = pd.DataFrame({
            'age': np.random.randint(18, 80, 100),
            'income': np.random.normal(50000, 20000, 100),
            'location': np.random.choice(['Urban', 'Suburban', 'Rural'], 100),
            'gender': np.random.choice(['M', 'F'], 100),
            'tech_score': np.random.randint(1, 11, 100)
        })
        
        # Ensure positive income values
        self.test_data['income'] = np.abs(self.test_data['income'])
        
        self.clusterer = ConstrainedKMedians(min_size_pct=0.05, max_size_pct=0.10)
    
    def test_initialization(self):
        """Test clusterer initialization"""
        self.assertEqual(self.clusterer.min_size_pct, 0.05)
        self.assertEqual(self.clusterer.max_size_pct, 0.10)
        self.assertIsNone(self.clusterer.labels_)
        self.assertIsNone(self.clusterer.cluster_centers_)
    
    def test_custom_constraints(self):
        """Test initialization with custom constraints"""
        custom_clusterer = ConstrainedKMedians(min_size_pct=0.08, max_size_pct=0.15)
        self.assertEqual(custom_clusterer.min_size_pct, 0.08)
        self.assertEqual(custom_clusterer.max_size_pct, 0.15)
    
    def test_fit_predict_basic(self):
        """Test basic fit_predict functionality"""
        labels = self.clusterer.fit_predict(self.test_data)
        
        # Check that labels are returned
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(self.test_data))
        
        # Check that labels are non-negative integers
        self.assertTrue(np.all(labels >= 0))
        self.assertTrue(np.all(labels == labels.astype(int)))
    
    def test_constraint_satisfaction(self):
        """Test that size constraints are satisfied"""
        labels = self.clusterer.fit_predict(self.test_data)
        
        # Calculate cluster sizes
        unique_labels, counts = np.unique(labels, return_counts=True)
        percentages = counts / len(self.test_data) * 100
        
        # Check constraints
        min_pct = self.clusterer.min_size_pct * 100
        max_pct = self.clusterer.max_size_pct * 100
        
        for pct in percentages:
            self.assertGreaterEqual(pct, min_pct - 0.1)  # Small tolerance for rounding
            self.assertLessEqual(pct, max_pct + 0.1)
    
    def test_cluster_centers_generation(self):
        """Test that cluster centers are generated"""
        labels = self.clusterer.fit_predict(self.test_data)
        
        self.assertIsNotNone(self.clusterer.cluster_centers_)
        self.assertIsInstance(self.clusterer.cluster_centers_, np.ndarray)
        
        # Number of centers should match number of clusters
        n_clusters = len(np.unique(labels))
        self.assertEqual(len(self.clusterer.cluster_centers_), n_clusters)
    
    def test_minimum_clusters(self):
        """Test with very small dataset requiring minimum clusters"""
        small_data = self.test_data.head(20)  # Only 20 samples
        labels = self.clusterer.fit_predict(small_data)
        
        # Should create at least 2 clusters (20 samples / 10% max = 2 clusters min)
        n_clusters = len(np.unique(labels))
        self.assertGreaterEqual(n_clusters, 2)
    
    def test_large_dataset(self):
        """Test with larger dataset"""
        # Create larger dataset
        large_data = pd.DataFrame({
            'age': np.random.randint(18, 80, 1000),
            'income': np.abs(np.random.normal(50000, 20000, 1000)),
            'score': np.random.randint(1, 11, 1000)
        })
        
        labels = self.clusterer.fit_predict(large_data)
        
        # Check constraints still hold
        unique_labels, counts = np.unique(labels, return_counts=True)
        percentages = counts / len(large_data) * 100
        
        min_pct = self.clusterer.min_size_pct * 100
        max_pct = self.clusterer.max_size_pct * 100
        
        for pct in percentages:
            self.assertGreaterEqual(pct, min_pct - 0.1)
            self.assertLessEqual(pct, max_pct + 0.1)
    
    def test_categorical_data_handling(self):
        """Test handling of categorical data"""
        categorical_data = pd.DataFrame({
            'category_a': np.random.choice(['A', 'B', 'C'], 100),
            'category_b': np.random.choice(['X', 'Y'], 100),
            'numeric': np.random.randn(100)
        })
        
        labels = self.clusterer.fit_predict(categorical_data)
        
        # Should handle categorical data without errors
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(categorical_data))
    
    def test_all_categorical_data(self):
        """Test with only categorical data"""
        cat_only_data = pd.DataFrame({
            'location': np.random.choice(['Urban', 'Suburban', 'Rural'], 100),
            'education': np.random.choice(['High School', 'College', 'Graduate'], 100),
            'employment': np.random.choice(['Full-time', 'Part-time', 'Unemployed'], 100)
        })
        
        labels = self.clusterer.fit_predict(cat_only_data)
        
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(cat_only_data))
    
    def test_single_column_data(self):
        """Test with single column"""
        single_col_data = pd.DataFrame({
            'score': np.random.randn(100)
        })
        
        labels = self.clusterer.fit_predict(single_col_data)
        
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(single_col_data))
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = pd.DataFrame()
        
        with self.assertRaises((ValueError, IndexError)):
            self.clusterer.fit_predict(empty_data)
    
    def test_score_calculation(self):
        """Test internal scoring mechanism"""
        labels = self.clusterer.fit_predict(self.test_data)
        
        # The clusterer should have calculated some score
        # This is mostly to ensure the method doesn't crash
        self.assertIsInstance(labels, np.ndarray)
    
    def test_median_calculation(self):
        """Test median center calculation"""
        labels = self.clusterer.fit_predict(self.test_data)
        centers = self.clusterer.cluster_centers_
        
        # Centers should be numeric
        self.assertTrue(np.all(np.isfinite(centers)))
        
        # Number of features in centers should match processed data
        n_clusters = len(np.unique(labels))
        self.assertEqual(centers.shape[0], n_clusters)
    
    def test_reproducibility(self):
        """Test that results are reproducible with same random seed"""
        # First run
        clusterer1 = ConstrainedKMedians(min_size_pct=0.05, max_size_pct=0.10)
        labels1 = clusterer1.fit_predict(self.test_data.copy())
        
        # Second run with same data
        clusterer2 = ConstrainedKMedians(min_size_pct=0.05, max_size_pct=0.10)
        labels2 = clusterer2.fit_predict(self.test_data.copy())
        
        # Labels might be permuted but cluster assignments should be similar
        # Check that number of clusters is the same
        self.assertEqual(len(np.unique(labels1)), len(np.unique(labels2)))


class TestConstrainedKMediansEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.clusterer = ConstrainedKMedians()
    
    def test_very_tight_constraints(self):
        """Test with very tight constraints that might be impossible"""
        tight_clusterer = ConstrainedKMedians(min_size_pct=0.09, max_size_pct=0.10)
        
        # Small dataset where tight constraints might be hard to satisfy
        small_data = pd.DataFrame({
            'value': list(range(25))  # 25 samples
        })
        
        labels = tight_clusterer.fit_predict(small_data)
        
        # Should still produce valid results, even if constraints are relaxed
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(small_data))
    
    def test_impossible_constraints(self):
        """Test with mathematically impossible constraints"""
        # Constraints that would require fractional samples
        impossible_clusterer = ConstrainedKMedians(min_size_pct=0.08, max_size_pct=0.09)
        
        tiny_data = pd.DataFrame({
            'value': list(range(10))  # 10 samples
        })
        
        # Should handle gracefully
        labels = impossible_clusterer.fit_predict(tiny_data)
        self.assertIsInstance(labels, np.ndarray)
    
    def test_all_identical_data(self):
        """Test with identical data points"""
        identical_data = pd.DataFrame({
            'value': [5.0] * 100,
            'category': ['A'] * 100
        })
        
        labels = self.clusterer.fit_predict(identical_data)
        
        # Should handle identical data without crashing
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(identical_data))
    
    def test_missing_values(self):
        """Test handling of missing values"""
        data_with_nan = pd.DataFrame({
            'value1': [1, 2, np.nan, 4, 5] * 20,
            'value2': [np.nan, 2, 3, 4, 5] * 20
        })
        
        # Should either handle NaN or raise clear error
        try:
            labels = self.clusterer.fit_predict(data_with_nan)
            self.assertIsInstance(labels, np.ndarray)
        except (ValueError, TypeError) as e:
            # Acceptable to raise error for NaN values
            self.assertIn('NaN', str(e).lower() + str(type(e).__name__).lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)