"""
Unit tests for Enhanced Audience API
Tests all new functionality including data types, CSV export, and enhanced workflow
"""

import unittest
import json
import os
import sys
import tempfile
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from api.enhanced_audience_api import (
    app, 
    EnhancedWorkflowState,
    generate_descriptive_segment_names,
    extract_dominant_traits,
    analyze_group_characteristics
)


class TestEnhancedAudienceAPI(unittest.TestCase):
    """Test enhanced audience API functionality"""
    
    def setUp(self):
        """Set up test client and mock data"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock session data
        self.test_session_id = "test-session-123"
        self.test_audience_id = "test-audience-456"
        
    def test_enhanced_workflow_state(self):
        """Test EnhancedWorkflowState with new attributes"""
        state = EnhancedWorkflowState()
        
        # Test initialization
        self.assertEqual(state.current_step, "initial")
        self.assertIsNone(state.data_type)
        self.assertIsNone(state.subtype)
        self.assertIsNone(state.audience_id)
        self.assertFalse(state.export_ready)
        
        # Test setting attributes
        state.data_type = "first_party"
        state.subtype = "rampid"
        state.audience_id = "test-123"
        state.export_ready = True
        
        self.assertEqual(state.data_type, "first_party")
        self.assertEqual(state.subtype, "rampid")
        self.assertEqual(state.audience_id, "test-123")
        self.assertTrue(state.export_ready)
    
    def test_generate_descriptive_segment_names(self):
        """Test segment name generation"""
        segments = [
            {'group_id': 0, 'size': 100, 'size_percentage': 10},
            {'group_id': 1, 'size': 150, 'size_percentage': 15}
        ]
        
        # Test with environmental query
        query = "environmentally conscious millennials with high disposable income"
        named_segments = generate_descriptive_segment_names(segments, query)
        
        self.assertEqual(len(named_segments), 2)
        self.assertIn('name', named_segments[0])
        self.assertIsInstance(named_segments[0]['name'], str)
        
        # Check that names are different
        self.assertNotEqual(named_segments[0]['name'], named_segments[1]['name'])
        
        # Test with keywords
        for segment in named_segments:
            # Should have meaningful names
            self.assertGreater(len(segment['name']), 5)
            self.assertNotIn('Segment 0', segment['name'])
    
    def test_extract_dominant_traits(self):
        """Test dominant trait extraction"""
        segment = {
            'characteristics': {
                'income': {
                    'type': 'numeric',
                    'mean': 85000
                },
                'location': {
                    'type': 'categorical',
                    'dominant_value': 'Urban',
                    'dominant_percentage': 75
                },
                'age': {
                    'type': 'numeric',
                    'mean': 28
                }
            }
        }
        
        traits = extract_dominant_traits(segment)
        
        self.assertIsInstance(traits, list)
        self.assertLessEqual(len(traits), 3)
        
        # Should identify high income
        self.assertTrue(any('High Income' in trait for trait in traits))
        # Should identify young adults
        self.assertTrue(any('Young Adults' in trait for trait in traits))
    
    def test_start_session_endpoint(self):
        """Test session initialization"""
        response = self.client.post('/api/nl/start_session')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('session_id', data)
        self.assertEqual(data['status'], 'ready')
        self.assertIn('message', data)
    
    def test_process_nl_request_with_data_type(self):
        """Test processing with data type selection"""
        # Start session
        session_response = self.client.post('/api/nl/start_session')
        session_data = json.loads(session_response.data)
        session_id = session_data['session_id']
        
        # Process with data type
        process_data = {
            'session_id': session_id,
            'action': 'process',
            'payload': {
                'input': 'find environmentally conscious millennials',
                'data_type': 'first_party',
                'subtype': 'rampid'
            }
        }
        
        response = self.client.post(
            '/api/nl/process',
            data=json.dumps(process_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return suggested variables
        self.assertEqual(data['status'], 'variables_suggested')
        self.assertIn('suggested_variables', data)
        self.assertIn('total_suggested', data)
        self.assertEqual(data['data_type'], 'first_party')
    
    @patch('api.enhanced_audience_api.data_retriever')
    @patch('api.enhanced_audience_api.clusterer')
    def test_complete_workflow(self, mock_clusterer, mock_retriever):
        """Test complete workflow from query to segments"""
        # Mock data
        mock_data = pd.DataFrame({
            'var1': [1, 2, 3, 4, 5],
            'var2': ['A', 'B', 'A', 'B', 'A'],
            'Group': [0, 0, 1, 1, 0]
        })
        mock_retriever.fetch_data.return_value = mock_data.drop('Group', axis=1)
        mock_clusterer.fit_predict.return_value = mock_data['Group'].values
        
        # Start session
        session_response = self.client.post('/api/nl/start_session')
        session_id = json.loads(session_response.data)['session_id']
        
        # Mock that variables are already suggested
        from api.enhanced_audience_api import sessions
        sessions[session_id].suggested_variables = [
            {'code': 'var1', 'type': 'numeric'},
            {'code': 'var2', 'type': 'categorical'}
        ]
        sessions[session_id].user_prompt = "test query"
        sessions[session_id].current_step = 'variables_suggested'  # Set correct state
        
        # Confirm variables
        confirm_data = {
            'session_id': session_id,
            'action': 'process',
            'payload': {
                'input': 'use these variables: var1, var2'
            }
        }
        
        response = self.client.post(
            '/api/nl/process',
            data=json.dumps(confirm_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['status'], 'complete')
        self.assertIn('segments', data)
        self.assertIn('audience_id', data)
        self.assertGreater(len(data['segments']), 0)
        
        # Check segment structure
        segment = data['segments'][0]
        self.assertIn('name', segment)
        self.assertIn('size', segment)
        self.assertIn('size_percentage', segment)
        self.assertIn('dominantTraits', segment)
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        # Create a mock session with data
        from api.enhanced_audience_api import sessions
        
        state = EnhancedWorkflowState()
        state.data = pd.DataFrame({
            'var1': [1, 2, 3],
            'var2': ['A', 'B', 'C'],
            'Group': [0, 1, 0]
        })
        state.user_prompt = "test query"
        state.segments = [
            {'group_id': 0, 'size': 2, 'size_percentage': 66.7, 'name': 'Test Segment 1'},
            {'group_id': 1, 'size': 1, 'size_percentage': 33.3, 'name': 'Test Segment 2'}
        ]
        state.audience_id = "test-export-123"
        
        sessions["test-export-123"] = state
        
        # Request export
        response = self.client.get('/api/export/test-export-123?format=csv')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith('text/csv'))
        
        # Check CSV content
        csv_content = response.data.decode('utf-8')
        lines = csv_content.split('\n')
        
        # Should have metadata headers
        self.assertIn('# Audience Export', lines[0])
        self.assertIn('# Query: test query', csv_content)
        self.assertIn('# Segment Summary:', csv_content)
        
        # Should have data
        self.assertIn('var1,var2,Group', csv_content)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('components', data)
        self.assertIn('variable_selector', data['components'])
        self.assertIn('data_retriever', data['components'])
        self.assertIn('sessions_active', data['components'])
    
    def test_distribute_endpoint(self):
        """Test distribution endpoint"""
        distribute_data = {
            'audience_id': 'test-123',
            'platforms': ['Facebook', 'Google', 'TheTradeDesk']
        }
        
        response = self.client.post(
            '/api/distribute',
            data=json.dumps(distribute_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 3)
        
        # Check result structure
        for result in data['results']:
            self.assertIn('platform', result)
            self.assertIn('status', result)
            self.assertIn('records_sent', result)
            self.assertIn('match_rate', result)
            self.assertEqual(result['status'], 'success')
    
    def test_analyze_group_characteristics(self):
        """Test group characteristic analysis"""
        group_data = pd.DataFrame({
            'numeric_var': [1, 2, 3, 4, 5],
            'categorical_var': ['A', 'A', 'B', 'A', 'B'],
            'Group': [0, 0, 0, 0, 0]
        })
        
        chars = analyze_group_characteristics(group_data)
        
        self.assertIn('numeric_var', chars)
        self.assertIn('categorical_var', chars)
        self.assertNotIn('Group', chars)
        
        # Check numeric characteristics
        num_char = chars['numeric_var']
        self.assertEqual(num_char['type'], 'numeric')
        self.assertIn('mean', num_char)
        self.assertIn('median', num_char)
        self.assertIn('std', num_char)
        
        # Check categorical characteristics
        cat_char = chars['categorical_var']
        self.assertEqual(cat_char['type'], 'categorical')
        self.assertIn('dominant_value', cat_char)
        self.assertIn('dominant_percentage', cat_char)
        self.assertIn('distribution', cat_char)


class TestEnhancedWorkflowIntegration(unittest.TestCase):
    """Integration tests for enhanced workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('api.enhanced_audience_api.variable_selector')
    def test_variable_selection_with_scoring(self, mock_selector):
        """Test enhanced variable selection with scoring"""
        # Mock variable selector response
        mock_selector.analyze_request.return_value = [
            {
                'code': 'ENV_CONSCIOUS',
                'description': 'Environmental consciousness score',
                'type': 'psychographic',
                'relevance_score': 8.5,
                'dataAvailability': {
                    'first_party': True,
                    'third_party': True,
                    'clean_room': False
                }
            },
            {
                'code': 'AGE_RANGE',
                'description': 'Age range millennials',
                'type': 'demographic',
                'relevance_score': 7.2,
                'dataAvailability': {
                    'first_party': True,
                    'third_party': False,
                    'clean_room': True
                }
            }
        ]
        
        # Start session and process
        session_resp = self.client.post('/api/nl/start_session')
        session_id = json.loads(session_resp.data)['session_id']
        
        process_data = {
            'session_id': session_id,
            'action': 'process',
            'payload': {
                'input': 'environmentally conscious millennials',
                'data_type': 'first_party'
            }
        }
        
        response = self.client.post(
            '/api/nl/process',
            data=json.dumps(process_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        # Verify grouped variables
        self.assertIn('suggested_variables', data)
        self.assertIn('psychographic', data['suggested_variables'])
        self.assertIn('demographic', data['suggested_variables'])
        
        # Check data availability is included
        psych_vars = data['suggested_variables']['psychographic']
        self.assertGreater(len(psych_vars), 0)
        self.assertIn('dataAvailability', psych_vars[0])
    
    def test_error_handling(self):
        """Test error handling in API"""
        # Test invalid session
        response = self.client.post(
            '/api/nl/process',
            data=json.dumps({
                'session_id': 'invalid-session',
                'action': 'process',
                'payload': {}
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Test export with non-existent audience
        response = self.client.get('/api/export/non-existent-audience')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()