"""
Test suite for Enhanced Variable Picker API Integration
Tests the enhanced semantic search functionality and integration with the Natural Language Multi-Variate Audience Builder
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI
from activation_manager.core.enhanced_semantic_search import EnhancedSemanticSearch


class TestEnhancedVariablePickerAPI:
    """Test enhanced variable picker API functionality"""
    
    @pytest.fixture
    def mock_variables(self):
        """Sample variables for testing"""
        return [
            {
                'code': 'AGE_25_34',
                'VarId': 'AGE_25_34',
                'name': 'Age 25-34 (Millennials)',
                'description': 'Millennials age group',
                'category': 'Demographics',
                'dataType': 'demographic',
                'Product': 'DaaS',
                'Theme': 'Age',
                'Domain': 'Individual'
            },
            {
                'code': 'ONLINE_SHOPPER',
                'VarId': 'ONLINE_SHOPPER',
                'name': 'Frequent Online Shopper',
                'description': 'Shops online frequently',
                'category': 'Behavior',
                'dataType': 'behavioral',
                'Product': 'DaaS',
                'Theme': 'Shopping',
                'Domain': 'Household'
            },
            {
                'code': 'HIGH_INCOME',
                'VarId': 'HIGH_INCOME',
                'name': 'High Income Household',
                'description': 'Household income over $100k',
                'category': 'Demographics',
                'dataType': 'demographic',
                'Product': 'DaaS',
                'Theme': 'Income',
                'Domain': 'Household'
            }
        ]
    
    @pytest.fixture
    def api_instance(self, mock_variables):
        """Create API instance with mocked data"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader') as mock_loader:
            # Mock the parquet loader
            mock_loader_instance = MagicMock()
            mock_loader_instance.get_all_variables.return_value = mock_variables
            mock_loader_instance.variables_df = MagicMock()
            mock_loader_instance.variables_df.empty = False
            mock_loader.return_value = mock_loader_instance
            
            # Create API instance
            api = EnhancedVariablePickerAPI()
            
            # Mock the enhanced search
            api.enhanced_search = MagicMock()
            api.enhanced_search.search.return_value = {
                'results': mock_variables[:2],
                'total_found': 2,
                'query_context': {'original_query': 'test'},
                'search_methods': {'semantic': True, 'keyword': True}
            }
            
            return api
    
    def test_initialization_with_parquet(self):
        """Test API initializes with Parquet loader"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader') as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.get_all_variables.return_value = [{'code': 'TEST'}]
            mock_loader_instance.variables_df = MagicMock()
            mock_loader_instance.variables_df.empty = False
            mock_loader.return_value = mock_loader_instance
            
            api = EnhancedVariablePickerAPI()
            
            assert api.enhanced_search is not None
            mock_loader.assert_called_once()
    
    def test_search_variables_basic(self, api_instance):
        """Test basic variable search"""
        results = api_instance.search_variables(
            query="young millennials",
            top_k=50
        )
        
        assert 'results' in results
        assert 'total_found' in results
        assert results['total_found'] == 2
        assert len(results['results']) == 2
    
    def test_search_variables_with_filters(self, api_instance):
        """Test search with semantic and keyword filters"""
        results = api_instance.search_variables(
            query="online shopping behavior",
            top_k=10,
            use_semantic=True,
            use_keyword=False
        )
        
        api_instance.enhanced_search.search.assert_called_with(
            query="online shopping behavior",
            top_k=10,
            use_semantic=True,
            use_keyword=False,
            filters=None
        )
    
    def test_search_empty_query(self, api_instance):
        """Test search with empty query returns empty results"""
        api_instance.enhanced_search = None
        api_instance.variable_selector = None
        
        results = api_instance.search_variables(query="", top_k=50)
        
        assert results['results'] == []
        assert results['total_found'] == 0
        assert 'error' in results
    
    def test_fallback_to_variable_selector(self, api_instance):
        """Test fallback to basic variable selector when enhanced search fails"""
        # Disable enhanced search
        api_instance.enhanced_search = None
        
        # Mock variable selector
        api_instance.variable_selector = MagicMock()
        api_instance.variable_selector.search.return_value = [
            {'code': 'FALLBACK_VAR', 'description': 'Fallback variable'}
        ]
        
        results = api_instance.search_variables(query="test fallback", top_k=20)
        
        assert 'results' in results
        assert len(results['results']) == 1
        assert results['results'][0]['code'] == 'FALLBACK_VAR'
        
        api_instance.variable_selector.search.assert_called_with(
            query="test fallback",
            top_k=20,
            use_semantic=True,
            use_keyword=True
        )
    
    def test_get_variable_stats(self, api_instance, mock_variables):
        """Test variable statistics generation"""
        # Setup enhanced search with proper variable objects
        api_instance.enhanced_search.variables = []
        for var in mock_variables:
            mock_var = MagicMock()
            mock_var.theme = var.get('Theme', 'Unknown')
            mock_var.product = var.get('Product', 'Unknown')
            mock_var.domain = var.get('Domain', 'Unknown')
            api_instance.enhanced_search.variables.append(mock_var)
        
        api_instance.enhanced_search.config = MagicMock()
        api_instance.enhanced_search.config.default_top_k = 50
        api_instance.enhanced_search.config.hybrid_weight_semantic = 0.7
        api_instance.enhanced_search.config.hybrid_weight_keyword = 0.3
        
        stats = api_instance.get_variable_stats()
        
        assert 'total_variables' in stats
        assert stats['total_variables'] == 3
        assert 'themes' in stats
        assert 'products' in stats
        assert 'domains' in stats
        assert 'search_config' in stats
    
    def test_search_by_category(self, api_instance, mock_variables):
        """Test searching variables by category"""
        # Setup variables in enhanced search
        api_instance.enhanced_search.variables = []
        for var in mock_variables:
            mock_var = MagicMock()
            mock_var.category = var.get('category', '')
            mock_var.to_dict = MagicMock(return_value=var)
            api_instance.enhanced_search.variables.append(mock_var)
        
        results = api_instance.search_by_category('Demographics', top_k=10)
        
        assert len(results) == 2  # AGE_25_34 and HIGH_INCOME
        assert all('Demographics' in r.get('category', '') for r in results)
    
    def test_get_variable_by_id(self, api_instance, mock_variables):
        """Test getting specific variable by ID"""
        # Setup variable lookup
        api_instance.enhanced_search.variable_lookup = {}
        for var in mock_variables:
            mock_var = MagicMock()
            mock_var.to_dict = MagicMock(return_value=var)
            api_instance.enhanced_search.variable_lookup[var['code']] = mock_var
        
        result = api_instance.get_variable_by_id('AGE_25_34')
        
        assert result is not None
        assert result['code'] == 'AGE_25_34'
        assert result['name'] == 'Age 25-34 (Millennials)'
    
    def test_csv_fallback_initialization(self):
        """Test fallback to CSV loader when Parquet fails"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedParquetLoader') as mock_parquet:
            # Make parquet loader fail
            mock_parquet.side_effect = Exception("Parquet load failed")
            
            with patch('activation_manager.api.enhanced_variable_picker_api.CSVVariableLoader') as mock_csv:
                # Mock CSV loader success
                mock_csv_instance = MagicMock()
                mock_df = MagicMock()
                mock_df.to_dict.return_value = [{'code': 'CSV_VAR'}]
                mock_csv_instance.load_variables.return_value = mock_df
                mock_csv.return_value = mock_csv_instance
                
                with patch('pathlib.Path.exists', return_value=True):
                    api = EnhancedVariablePickerAPI()
                    
                    # Should have tried CSV loader
                    mock_csv.assert_called()


class TestFlaskIntegration:
    """Test Flask API endpoint integration"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test app"""
        from flask import Flask
        from activation_manager.api.enhanced_variable_picker_api import create_enhanced_variable_picker_blueprint
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Register blueprint
        bp = create_enhanced_variable_picker_blueprint()
        app.register_blueprint(bp, url_prefix='/api/enhanced-picker')
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_search_endpoint(self, client):
        """Test /search endpoint"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI') as mock_api_class:
            # Setup mock
            mock_api = MagicMock()
            mock_api.search_variables.return_value = {
                'results': [{'code': 'TEST_VAR'}],
                'total_found': 1
            }
            mock_api_class.return_value = mock_api
            
            # Make request
            response = client.post('/api/enhanced-picker/search', 
                                 json={'query': 'test search', 'top_k': 25})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'results' in data
            assert data['total_found'] == 1
    
    def test_search_endpoint_no_query(self, client):
        """Test /search endpoint with missing query"""
        response = client.post('/api/enhanced-picker/search', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_stats_endpoint(self, client):
        """Test /stats endpoint"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI') as mock_api_class:
            # Setup mock
            mock_api = MagicMock()
            mock_api.get_variable_stats.return_value = {
                'total_variables': 100,
                'themes': {'Demographics': 50}
            }
            mock_api_class.return_value = mock_api
            
            response = client.get('/api/enhanced-picker/stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_variables'] == 100
    
    def test_variable_by_id_endpoint(self, client):
        """Test /variable/<id> endpoint"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI') as mock_api_class:
            # Setup mock
            mock_api = MagicMock()
            mock_api.get_variable_by_id.return_value = {
                'code': 'TEST_ID',
                'name': 'Test Variable'
            }
            mock_api_class.return_value = mock_api
            
            response = client.get('/api/enhanced-picker/variable/TEST_ID')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['code'] == 'TEST_ID'
    
    def test_category_search_endpoint(self, client):
        """Test /category/<category> endpoint"""
        with patch('activation_manager.api.enhanced_variable_picker_api.EnhancedVariablePickerAPI') as mock_api_class:
            # Setup mock
            mock_api = MagicMock()
            mock_api.search_by_category.return_value = [
                {'code': 'CAT_VAR', 'category': 'TestCategory'}
            ]
            mock_api_class.return_value = mock_api
            
            response = client.get('/api/enhanced-picker/category/TestCategory?top_k=5')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['category'] == 'TestCategory'
            assert len(data['results']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])