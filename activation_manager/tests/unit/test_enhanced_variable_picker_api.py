"""
Unit tests for Enhanced Variable Picker API
Tests the API integration layer with parquet loader and enhanced search
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os

from activation_manager.api.enhanced_variable_picker_api import (
    EnhancedVariablePickerAPI, create_enhanced_variable_picker_blueprint
)


class TestEnhancedVariablePickerAPI(unittest.TestCase):
    """Test the Enhanced Variable Picker API"""
    
    def setUp(self):
        """Set up test environment"""
        # Disable OpenAI for tests
        self.api = None
    
    @patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader')
    @patch('activation_manager.api.enhanced_variable_picker_api.VariableSelector')
    def test_initialization_with_parquet(self, mock_selector, mock_parquet):
        """Test API initialization with parquet data"""
        # Mock parquet loader
        mock_loader = MagicMock()
        mock_loader.variables_df = MagicMock()
        mock_loader.variables_df.empty = False
        mock_loader.get_all_variables.return_value = [
            {'code': 'VAR1', 'description': 'Test Variable 1'},
            {'code': 'VAR2', 'description': 'Test Variable 2'}
        ]
        mock_parquet.return_value = mock_loader
        
        # Mock variable selector
        mock_sel = MagicMock()
        mock_sel.embeddings = None
        mock_selector.return_value = mock_sel
        
        # Initialize API
        api = EnhancedVariablePickerAPI()
        
        # Should use parquet loader
        mock_parquet.assert_called_once()
        self.assertIsNotNone(api.enhanced_search)
    
    @patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader')
    @patch('activation_manager.api.enhanced_variable_picker_api.VariableSelector')
    def test_fallback_to_variable_selector(self, mock_selector, mock_parquet):
        """Test fallback to VariableSelector when parquet fails"""
        # Mock failed parquet loader
        mock_parquet.side_effect = Exception("Parquet load failed")
        
        # Mock successful variable selector
        mock_sel = MagicMock()
        mock_sel.variables = {
            'VAR1': {'description': 'Test Variable 1'},
            'VAR2': {'description': 'Test Variable 2'}
        }
        mock_sel.embeddings = None
        mock_selector.return_value = mock_sel
        
        # Initialize API
        api = EnhancedVariablePickerAPI()
        
        # Should fall back to variable selector
        mock_selector.assert_called()
        self.assertIsNotNone(api.enhanced_search)
    
    @patch('activation_manager.api.enhanced_variable_picker_api.CSVVariableLoader')
    def test_fallback_to_csv(self, mock_csv):
        """Test fallback to CSV when other methods fail"""
        # Mock CSV loader
        mock_loader = MagicMock()
        mock_loader.load_variables.return_value = MagicMock()
        mock_loader.load_variables.return_value.to_dict.return_value = [
            {'code': 'VAR1', 'description': 'CSV Variable 1'}
        ]
        mock_csv.return_value = mock_loader
        
        # Patch to simulate parquet and selector failures
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader') as mock_parquet:
            mock_parquet.side_effect = Exception("Parquet failed")
            
            with patch('activation_manager.api.enhanced_variable_picker_api.VariableSelector') as mock_selector:
                mock_selector.return_value.variables = {}
                
                # Mock path exists
                with patch('pathlib.Path.exists', return_value=True):
                    api = EnhancedVariablePickerAPI()
                    
                    # Should use CSV loader
                    mock_csv.assert_called()
    
    def test_search_variables(self):
        """Test search functionality"""
        api = EnhancedVariablePickerAPI()
        
        # Mock enhanced search
        mock_search = MagicMock()
        mock_search.search.return_value = {
            'results': [
                {'code': 'VAR1', 'description': 'Found Variable', 'score': 0.9}
            ],
            'total_found': 1,
            'query_context': {'original_query': 'test query'}
        }
        api.enhanced_search = mock_search
        
        # Test search
        results = api.search_variables('test query', top_k=10)
        
        self.assertIn('results', results)
        self.assertEqual(len(results['results']), 1)
        self.assertEqual(results['results'][0]['code'], 'VAR1')
        
        # Verify search was called correctly
        mock_search.search.assert_called_with(
            query='test query',
            top_k=10,
            use_semantic=True,
            use_keyword=True,
            filters=None
        )
    
    def test_search_with_filters(self):
        """Test search with filters"""
        api = EnhancedVariablePickerAPI()
        
        # Mock enhanced search
        mock_search = MagicMock()
        mock_search.search.return_value = {
            'results': [],
            'total_found': 0
        }
        api.enhanced_search = mock_search
        
        # Test search with filters
        filters = {'theme': 'Demographic', 'product': 'DemoStats'}
        api.search_variables('age groups', filters=filters)
        
        # Verify filters were passed
        mock_search.search.assert_called_with(
            query='age groups',
            top_k=50,
            use_semantic=True,
            use_keyword=True,
            filters=filters
        )
    
    def test_search_fallback(self):
        """Test search fallback when enhanced search not available"""
        api = EnhancedVariablePickerAPI()
        api.enhanced_search = None
        
        # Mock variable selector
        mock_selector = MagicMock()
        mock_selector.search.return_value = [
            {'code': 'VAR1', 'description': 'Fallback Result'}
        ]
        api.variable_selector = mock_selector
        
        # Test search
        results = api.search_variables('test', top_k=10)
        
        self.assertIn('results', results)
        self.assertEqual(len(results['results']), 1)
        mock_selector.search.assert_called_once()
    
    def test_get_variable_stats(self):
        """Test statistics retrieval"""
        api = EnhancedVariablePickerAPI()
        
        # Mock enhanced search with variables
        mock_search = MagicMock()
        mock_var1 = MagicMock()
        mock_var1.theme = 'Demographic'
        mock_var1.product = 'DemoStats'
        mock_var1.domain = 'demographic'
        
        mock_var2 = MagicMock()
        mock_var2.theme = 'Financial'
        mock_var2.product = 'FinIndex'
        mock_var2.domain = 'financial'
        
        mock_search.variables = [mock_var1, mock_var2]
        mock_search.config.default_top_k = 50
        mock_search.config.hybrid_weight_semantic = 0.7
        mock_search.config.hybrid_weight_keyword = 0.3
        api.enhanced_search = mock_search
        
        # Get stats
        stats = api.get_variable_stats()
        
        self.assertEqual(stats['total_variables'], 2)
        self.assertIn('themes', stats)
        self.assertIn('products', stats)
        self.assertIn('domains', stats)
        self.assertEqual(stats['themes']['Demographic'], 1)
        self.assertEqual(stats['themes']['Financial'], 1)
    
    def test_search_by_category(self):
        """Test category search"""
        api = EnhancedVariablePickerAPI()
        
        # Mock enhanced search
        mock_var1 = MagicMock()
        mock_var1.category = 'Income'
        mock_var1.to_dict.return_value = {
            'code': 'INC001',
            'description': 'High Income',
            'category': 'Income'
        }
        
        mock_var2 = MagicMock()
        mock_var2.category = 'Age'
        mock_var2.to_dict.return_value = {
            'code': 'AGE001',
            'description': 'Young Adults',
            'category': 'Age'
        }
        
        mock_search = MagicMock()
        mock_search.variables = [mock_var1, mock_var2]
        api.enhanced_search = mock_search
        
        # Search by category
        results = api.search_by_category('Income', top_k=10)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['code'], 'INC001')
    
    def test_get_variable_by_id(self):
        """Test direct variable lookup"""
        api = EnhancedVariablePickerAPI()
        
        # Mock enhanced search
        mock_var = MagicMock()
        mock_var.to_dict.return_value = {
            'code': 'VAR123',
            'description': 'Test Variable'
        }
        
        mock_search = MagicMock()
        mock_search.variable_lookup = {'VAR123': mock_var}
        api.enhanced_search = mock_search
        
        # Get variable
        result = api.get_variable_by_id('VAR123')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['code'], 'VAR123')
        
        # Test missing variable
        result_missing = api.get_variable_by_id('MISSING')
        self.assertIsNone(result_missing)


class TestFlaskBlueprint(unittest.TestCase):
    """Test Flask blueprint creation"""
    
    @patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI')
    def test_blueprint_creation(self, mock_api_class):
        """Test that blueprint is created correctly"""
        # Mock API instance
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Create blueprint
        bp = create_enhanced_variable_picker_blueprint(api_key='test-key')
        
        # Check blueprint properties
        self.assertEqual(bp.name, 'enhanced_variable_picker')
        
        # Check routes are registered
        routes = [rule.rule for rule in bp.url_map.iter_rules()]
        self.assertIn('/search', routes)
        self.assertIn('/stats', routes)
        self.assertIn('/variable/<var_id>', routes)
        self.assertIn('/category/<category>', routes)
    
    @patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI')
    def test_search_endpoint(self, mock_api_class):
        """Test search endpoint functionality"""
        # Mock API
        mock_api = MagicMock()
        mock_api.search_variables.return_value = {
            'results': [{'code': 'VAR1'}],
            'total_found': 1
        }
        mock_api_class.return_value = mock_api
        
        # Create blueprint and test client
        bp = create_enhanced_variable_picker_blueprint()
        
        # Create Flask app for testing
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(bp, url_prefix='/api')
        
        with app.test_client() as client:
            # Test valid search
            response = client.post('/api/search', 
                                 json={'query': 'test search', 'top_k': 25})
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('results', data)
            
            # Test missing query
            response = client.post('/api/search', json={})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()