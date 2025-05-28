"""
Unit tests for DataRetriever
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np
from audience_builder import DataRetriever


class TestDataRetriever(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary test data file
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_path = os.path.join(self.temp_dir, 'test_data.csv')
        
        # Create comprehensive test data
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'AGE_RANGE': np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'], 1000),
            'INCOME_LEVEL': np.random.choice(['<30k', '30-50k', '50-75k', '75-100k', '100k+'], 1000),
            'LOCATION_TYPE': np.random.choice(['Urban', 'Suburban', 'Rural'], 1000),
            'TECH_SCORE': np.random.randint(1, 11, 1000),
            'PURCHASE_FREQ': np.random.randint(0, 50, 1000),
            'GREEN_CONSCIOUS': np.random.choice([0, 1], 1000),
            'PostalCode': ['K1A' + str(i).zfill(3) for i in range(1000)],
            'PRIZM_SEGMENT': np.random.choice(['Young Digerati', 'Money & Brains', 'Kids & Cul-de-Sacs'], 1000),
            'LATITUDE': np.random.uniform(45.0, 46.0, 1000),
            'LONGITUDE': np.random.uniform(-76.0, -75.0, 1000),
            'EXTRA_COLUMN': np.random.randn(1000)
        })
        
        self.test_data.to_csv(self.test_data_path, index=False)
        
        # Initialize DataRetriever
        self.retriever = DataRetriever(self.test_data_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_path(self):
        """Test DataRetriever initialization with file path"""
        self.assertEqual(self.retriever.data_path, self.test_data_path)
        self.assertIsNone(self.retriever.data)  # Data not loaded yet
    
    def test_initialization_without_path(self):
        """Test DataRetriever initialization without file path"""
        retriever = DataRetriever()
        self.assertIsNone(retriever.data_path)
        self.assertIsNone(retriever.data)
    
    def test_load_data_success(self):
        """Test successful data loading"""
        self.retriever.load_data()
        
        self.assertIsNotNone(self.retriever.data)
        self.assertIsInstance(self.retriever.data, pd.DataFrame)
        self.assertEqual(len(self.retriever.data), 1000)
        self.assertGreater(len(self.retriever.data.columns), 0)
    
    def test_load_data_file_not_found(self):
        """Test loading data when file doesn't exist"""
        retriever = DataRetriever('/nonexistent/path.csv')
        
        with self.assertRaises(FileNotFoundError):
            retriever.load_data()
    
    def test_load_data_no_path(self):
        """Test loading data when no path is set"""
        retriever = DataRetriever()
        
        with self.assertRaises((ValueError, AttributeError)):
            retriever.load_data()
    
    def test_fetch_data_basic(self):
        """Test basic data fetching"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE', 'INCOME_LEVEL', 'TECH_SCORE']
        result = self.retriever.fetch_data(variables)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result.columns), len(variables))
        self.assertEqual(set(result.columns), set(variables))
        self.assertEqual(len(result), 1000)  # Should return all data by default
    
    def test_fetch_data_with_sample_size(self):
        """Test data fetching with sample size limit"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE', 'INCOME_LEVEL']
        sample_size = 100
        
        result = self.retriever.fetch_data(variables, sample_size)
        
        self.assertEqual(len(result), sample_size)
        self.assertEqual(set(result.columns), set(variables))
    
    def test_fetch_data_sample_larger_than_data(self):
        """Test fetching with sample size larger than available data"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE']
        sample_size = 2000  # Larger than our 1000 rows
        
        result = self.retriever.fetch_data(variables, sample_size)
        
        # Should return all available data
        self.assertEqual(len(result), 1000)
    
    def test_fetch_data_nonexistent_variables(self):
        """Test fetching data with variables that don't exist"""
        self.retriever.load_data()
        
        variables = ['NONEXISTENT_VAR1', 'NONEXISTENT_VAR2']
        result = self.retriever.fetch_data(variables)
        
        # Should return empty DataFrame or handle gracefully
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result.columns), 0)
    
    def test_fetch_data_mixed_existing_nonexistent(self):
        """Test fetching with mix of existing and non-existing variables"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE', 'NONEXISTENT_VAR', 'INCOME_LEVEL']
        result = self.retriever.fetch_data(variables)
        
        # Should return only existing variables
        expected_vars = ['AGE_RANGE', 'INCOME_LEVEL']
        self.assertEqual(set(result.columns), set(expected_vars))
    
    def test_fetch_data_empty_variable_list(self):
        """Test fetching with empty variable list"""
        self.retriever.load_data()
        
        result = self.retriever.fetch_data([])
        
        # Should return DataFrame with special columns (PostalCode, PRIZM_SEGMENT, etc.)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result.columns), 0)
        
        # Should include PostalCode and PRIZM_SEGMENT if available
        expected_special_cols = ['PostalCode', 'PRIZM_SEGMENT', 'LATITUDE', 'LONGITUDE']
        for col in expected_special_cols:
            if col in self.test_data.columns:
                self.assertIn(col, result.columns)
    
    def test_fetch_data_includes_special_columns(self):
        """Test that special columns are always included"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE']
        result = self.retriever.fetch_data(variables)
        
        # Should include requested variable plus special columns
        self.assertIn('AGE_RANGE', result.columns)
        
        # Should include special columns if they exist in data
        special_cols = ['PostalCode', 'PRIZM_SEGMENT', 'LATITUDE', 'LONGITUDE']
        for col in special_cols:
            if col in self.test_data.columns:
                self.assertIn(col, result.columns)
    
    def test_fetch_data_without_loading(self):
        """Test fetching data without loading first"""
        variables = ['AGE_RANGE']
        
        with self.assertRaises(AttributeError):
            self.retriever.fetch_data(variables)
    
    def test_fetch_data_reproducibility(self):
        """Test that fetching with same parameters gives consistent results"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE', 'INCOME_LEVEL']
        sample_size = 100
        
        # Fetch twice with same parameters
        result1 = self.retriever.fetch_data(variables, sample_size)
        result2 = self.retriever.fetch_data(variables, sample_size)
        
        # Should be identical due to random seed
        pd.testing.assert_frame_equal(result1, result2)
    
    def test_data_types_preservation(self):
        """Test that data types are preserved during fetching"""
        self.retriever.load_data()
        
        variables = ['AGE_RANGE', 'TECH_SCORE', 'GREEN_CONSCIOUS']
        result = self.retriever.fetch_data(variables)
        
        # Check that data types are reasonable
        self.assertTrue(result['AGE_RANGE'].dtype == 'object')  # Categorical
        self.assertTrue(pd.api.types.is_numeric_dtype(result['TECH_SCORE']))  # Numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(result['GREEN_CONSCIOUS']))  # Binary


class TestDataRetrieverWithRealData(unittest.TestCase):
    """Test DataRetriever with real synthetic data if available"""
    
    def setUp(self):
        """Set up with real data path if available"""
        self.real_data_path = "/Users/myles/Documents/Activation Manager/Synthetic_Data/output/synthetic_consumer_data_1000_20250525_155201.csv"
        
        if os.path.exists(self.real_data_path):
            self.retriever = DataRetriever(self.real_data_path)
            self.has_real_data = True
        else:
            self.has_real_data = False
    
    def test_load_real_data(self):
        """Test loading real synthetic data"""
        if not self.has_real_data:
            self.skipTest("Real synthetic data not available")
        
        self.retriever.load_data()
        
        self.assertIsNotNone(self.retriever.data)
        self.assertGreater(len(self.retriever.data), 0)
        self.assertGreater(len(self.retriever.data.columns), 10)  # Should have many columns
    
    def test_fetch_realistic_variables(self):
        """Test fetching realistic variable combinations"""
        if not self.has_real_data:
            self.skipTest("Real synthetic data not available")
        
        self.retriever.load_data()
        
        # Try to fetch some common variable patterns
        common_variables = [
            ['AGE', 'INCOME'],
            ['LOCATION_TYPE', 'FAMILY_SIZE'],
            ['EDUCATION', 'OCCUPATION']
        ]
        
        available_columns = self.retriever.data.columns.tolist()
        
        for var_set in common_variables:
            # Find actual column names that match patterns
            matching_vars = []
            for var in var_set:
                matches = [col for col in available_columns if var.lower() in col.lower()]
                if matches:
                    matching_vars.append(matches[0])
            
            if matching_vars:
                with self.subTest(variables=matching_vars):
                    result = self.retriever.fetch_data(matching_vars)
                    
                    self.assertIsInstance(result, pd.DataFrame)
                    self.assertGreater(len(result), 0)
                    self.assertEqual(len(result.columns), len(matching_vars))
    
    def test_performance_large_fetch(self):
        """Test performance with large data fetch"""
        if not self.has_real_data:
            self.skipTest("Real synthetic data not available")
        
        self.retriever.load_data()
        
        # Get all available columns
        all_columns = self.retriever.data.columns.tolist()
        
        # Remove special columns to avoid duplication
        regular_columns = [col for col in all_columns 
                          if col not in ['PostalCode', 'PRIZM_SEGMENT', 'LATITUDE', 'LONGITUDE']]
        
        # Test fetching many variables
        import time
        start_time = time.time()
        
        result = self.retriever.fetch_data(regular_columns[:20])  # First 20 columns
        
        end_time = time.time()
        
        # Should complete quickly
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)


class TestDataRetrieverEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_empty_csv_file(self):
        """Test with empty CSV file"""
        empty_file = os.path.join(self.temp_dir, 'empty.csv')
        
        # Create empty file
        with open(empty_file, 'w') as f:
            f.write('')
        
        retriever = DataRetriever(empty_file)
        
        with self.assertRaises((pd.errors.EmptyDataError, ValueError)):
            retriever.load_data()
    
    def test_malformed_csv(self):
        """Test with malformed CSV file"""
        malformed_file = os.path.join(self.temp_dir, 'malformed.csv')
        
        # Create malformed CSV
        with open(malformed_file, 'w') as f:
            f.write('col1,col2\n')
            f.write('val1\n')  # Missing column
            f.write('val2,val3,val4\n')  # Extra column
        
        retriever = DataRetriever(malformed_file)
        
        # Should either handle gracefully or raise clear error
        try:
            retriever.load_data()
            result = retriever.fetch_data(['col1'])
            self.assertIsInstance(result, pd.DataFrame)
        except (pd.errors.ParserError, ValueError):
            pass  # Acceptable to raise error for malformed data
    
    def test_csv_with_missing_values(self):
        """Test CSV with missing values"""
        csv_with_na = os.path.join(self.temp_dir, 'with_na.csv')
        
        # Create CSV with missing values
        with open(csv_with_na, 'w') as f:
            f.write('col1,col2,col3\n')
            f.write('1,2,3\n')
            f.write('4,,6\n')  # Missing value
            f.write('7,8,\n')  # Missing value
            f.write(',,\n')    # All missing
        
        retriever = DataRetriever(csv_with_na)
        retriever.load_data()
        
        result = retriever.fetch_data(['col1', 'col2'])
        
        # Should handle missing values gracefully
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)  # Should include all rows
    
    def test_unicode_and_special_characters(self):
        """Test with Unicode and special characters"""
        unicode_file = os.path.join(self.temp_dir, 'unicode.csv')
        
        # Create CSV with Unicode characters
        test_data = pd.DataFrame({
            'name': ['João', 'François', 'María', '测试'],
            'city': ['São Paulo', 'Montréal', 'México', '北京'],
            'value': [1, 2, 3, 4]
        })
        test_data.to_csv(unicode_file, index=False, encoding='utf-8')
        
        retriever = DataRetriever(unicode_file)
        retriever.load_data()
        
        result = retriever.fetch_data(['name', 'city'])
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
        # Check that Unicode characters are preserved
        self.assertIn('João', result['name'].values)


if __name__ == '__main__':
    unittest.main(verbosity=2)