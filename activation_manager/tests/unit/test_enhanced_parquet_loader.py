"""
Unit tests for Enhanced Parquet Loader
Tests loading, searching, and performance of parquet-based variable storage
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock, patch

from activation_manager.core.enhanced_parquet_loader import EnhancedParquetLoader


class TestEnhancedParquetLoader(unittest.TestCase):
    """Test suite for Enhanced Parquet Loader"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests"""
        # Create sample dataframe
        cls.sample_data = pd.DataFrame({
            'theme': ['Demographic'] * 5 + ['Financial'] * 5,
            'ProductName': ['DemoStats'] * 5 + ['Financial Index'] * 5,
            'SortOrder': range(1, 11),
            'code': [f'VAR_{i:03d}' for i in range(1, 11)],
            'description': [
                'Young adults age 18-24',
                'Middle age 35-44',
                'Senior citizens 65+',
                'Urban households',
                'Rural population',
                'High income over 150k',
                'Middle income 50-100k',
                'Low income under 30k',
                'Luxury spending',
                'Budget conscious'
            ],
            'category': ['Age'] * 3 + ['Geography'] * 2 + ['Income'] * 3 + ['Behavior'] * 2,
            'type': ['demographic'] * 5 + ['financial'] * 5,
            'context': ['Census data'] * 10,
            'Consumption Flag': ['Incidence'] * 10
        })
        
        # Add lowercase columns
        cls.sample_data['code_lower'] = cls.sample_data['code'].str.lower()
        cls.sample_data['description_lower'] = cls.sample_data['description'].str.lower()
        
        # Create temporary parquet file
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_parquet = Path(cls.temp_dir) / 'test_variables.parquet'
        cls.sample_data.to_parquet(cls.temp_parquet, index=False)
    
    def setUp(self):
        """Set up for each test"""
        self.loader = None
    
    def test_initialization_with_file(self):
        """Test loader initialization with valid parquet file"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        self.assertIsNotNone(loader.variables_df)
        self.assertEqual(len(loader.variables_df), 10)
        self.assertEqual(len(loader.get_all_variables()), 10)
        self.assertTrue(loader.load_variables())
    
    def test_initialization_without_file(self):
        """Test loader initialization with missing file"""
        loader = EnhancedParquetLoader('/nonexistent/path.parquet')
        
        self.assertIsNone(loader.variables_df)
        self.assertEqual(len(loader.get_all_variables()), 0)
        self.assertFalse(loader.load_variables())
    
    def test_lookup_structures(self):
        """Test that lookup structures are built correctly"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        # Test variables dict
        self.assertEqual(len(loader.variables_dict), 10)
        self.assertIn('VAR_001', loader.variables_dict)
        
        # Test category index
        self.assertEqual(len(loader.category_index['Age']), 3)
        self.assertEqual(len(loader.category_index['Income']), 3)
        
        # Test theme index
        self.assertEqual(len(loader.theme_index['Demographic']), 5)
        self.assertEqual(len(loader.theme_index['Financial']), 5)
    
    def test_get_variable_by_id(self):
        """Test direct variable lookup by ID"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        # Test existing variable
        var = loader.get_variable_by_id('VAR_001')
        self.assertIsNotNone(var)
        self.assertEqual(var['description'], 'Young adults age 18-24')
        
        # Test case insensitive lookup
        var_upper = loader.get_variable_by_id('var_001')
        self.assertIsNotNone(var_upper)
        
        # Test non-existent variable
        var_missing = loader.get_variable_by_id('MISSING')
        self.assertIsNone(var_missing)
    
    def test_search_functionality(self):
        """Test search with various queries"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        # Test 1: Search for age-related variables
        results = loader.search('age', limit=10)
        self.assertGreater(len(results), 0)
        self.assertIn('age', results[0]['description'].lower())
        
        # Test 2: Search for income
        results = loader.search('income', limit=5)
        self.assertEqual(len(results), 3)  # Should find all 3 income variables
        
        # Test 3: Multi-word search
        results = loader.search('high income', limit=5)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['code'], 'VAR_006')  # High income should be first
        
        # Test 4: Code search
        results = loader.search('VAR_001', limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['code'], 'VAR_001')
        
        # Test 5: No results
        results = loader.search('nonexistent query xyz', limit=5)
        self.assertEqual(len(results), 0)
    
    def test_search_scoring(self):
        """Test that search scoring works correctly"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        # Exact code match should score highest
        results = loader.search('VAR_001', limit=10)
        self.assertGreater(results[0]['search_score'], 100.0)  # Should be high score
        
        # Description match should score well
        results = loader.search('young adults', limit=10)
        self.assertGreater(results[0]['search_score'], 30)
    
    def test_get_variables_by_category(self):
        """Test category filtering"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        age_vars = loader.get_variables_by_category('Age')
        self.assertEqual(len(age_vars), 3)
        
        income_vars = loader.get_variables_by_category('Income')
        self.assertEqual(len(income_vars), 3)
        
        missing_vars = loader.get_variables_by_category('Missing')
        self.assertEqual(len(missing_vars), 0)
    
    def test_get_variables_by_theme(self):
        """Test theme filtering"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        demo_vars = loader.get_variables_by_theme('Demographic')
        self.assertEqual(len(demo_vars), 5)
        
        fin_vars = loader.get_variables_by_theme('Financial')
        self.assertEqual(len(fin_vars), 5)
    
    def test_get_stats(self):
        """Test statistics generation"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        stats = loader.get_stats()
        self.assertEqual(stats['total_variables'], 10)
        self.assertEqual(len(stats['themes']), 2)
        self.assertEqual(len(stats['products']), 2)
        self.assertEqual(stats['categories'], 4)  # Age, Geography, Income, Behavior
        self.assertIn('data_source', stats)
        self.assertIn('columns', stats)
    
    def test_to_dataframe(self):
        """Test dataframe export"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        df = loader.to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)
        # Should be a copy, not reference
        df.loc[0, 'code'] = 'MODIFIED'
        self.assertNotEqual(loader.variables_df.loc[0, 'code'], 'MODIFIED')
    
    def test_performance(self):
        """Test that operations are performant"""
        loader = EnhancedParquetLoader(str(self.temp_parquet))
        
        # Loading should be fast
        start = time.time()
        loader.load_variables()
        load_time = time.time() - start
        self.assertLess(load_time, 1.0)  # Should load in under 1 second
        
        # Search should be fast
        start = time.time()
        for _ in range(10):
            loader.search('income', limit=50)
        search_time = time.time() - start
        self.assertLess(search_time, 0.5)  # 10 searches in under 0.5 seconds
        
        # Direct lookup should be instant
        start = time.time()
        for i in range(1, 11):
            loader.get_variable_by_id(f'VAR_{i:03d}')
        lookup_time = time.time() - start
        self.assertLess(lookup_time, 0.01)  # Near instant
    
    def test_real_parquet_file(self):
        """Test with the actual parquet file if it exists"""
        real_parquet = Path("/Users/myles/Documents/Activation Manager/data/variables_2022_can.parquet")
        
        if real_parquet.exists():
            loader = EnhancedParquetLoader(str(real_parquet))
            
            # Should load full dataset
            self.assertEqual(len(loader.get_all_variables()), 49323)
            
            # Test real search
            results = loader.search('luxury vehicles', limit=10)
            self.assertGreater(len(results), 0)
            
            # Test stats
            stats = loader.get_stats()
            self.assertEqual(stats['total_variables'], 49323)
            self.assertEqual(len(stats['themes']), 5)
            self.assertEqual(len(stats['products']), 30)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(cls.temp_dir)


if __name__ == '__main__':
    unittest.main()