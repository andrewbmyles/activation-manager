"""
Unit tests for bug fixes implemented on May 25, 2025
Tests cover error handling, data validation, and edge cases
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from activation_manager.api.enhanced_audience_api import app, sessions, analyze_group_characteristics
from activation_manager.core.audience_builder import ConstrainedKMedians


class TestBugFixes(unittest.TestCase):
    """Test cases for specific bug fixes"""
    
    def setUp(self):
        """Set up test client and clear sessions"""
        self.app = app
        self.client = self.app.test_client()
        sessions.clear()
        
    def tearDown(self):
        """Clean up after each test"""
        sessions.clear()
        
    def test_confirm_action_handler(self):
        """Test that the confirm action properly handles confirmed variables"""
        # Start a session
        response = self.client.post('/api/nl/start_session',
                                   content_type='application/json')
        session_data = json.loads(response.data)
        session_id = session_data['session_id']
        
        # Mock the data retriever to return test data
        with patch('api.enhanced_audience_api.data_retriever.fetch_data') as mock_fetch:
            # Create test data
            test_data = pd.DataFrame({
                'VAR1': np.random.choice(['A', 'B', 'C'], 100),
                'VAR2': np.random.randn(100),
                'VAR3': np.random.choice([0, 1], 100)
            })
            mock_fetch.return_value = test_data
            
            # Test confirm action with proper payload
            response = self.client.post('/api/nl/process',
                                       json={
                                           'session_id': session_id,
                                           'action': 'confirm',
                                           'payload': {
                                               'confirmed_variables': ['VAR1', 'VAR2', 'VAR3']
                                           }
                                       },
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'complete')
            self.assertIn('segments', data)
            self.assertIn('audience_id', data)
            
    def test_confirm_action_no_variables(self):
        """Test confirm action with no variables returns error"""
        # Start a session
        response = self.client.post('/api/nl/start_session',
                                   content_type='application/json')
        session_data = json.loads(response.data)
        session_id = session_data['session_id']
        
        # Test confirm action with empty variables
        response = self.client.post('/api/nl/process',
                                   json={
                                       'session_id': session_id,
                                       'action': 'confirm',
                                       'payload': {
                                           'confirmed_variables': []
                                       }
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No variables to confirm')
        
    def test_confirm_action_no_data(self):
        """Test confirm action when no data is available"""
        # Start a session
        response = self.client.post('/api/nl/start_session',
                                   content_type='application/json')
        session_data = json.loads(response.data)
        session_id = session_data['session_id']
        
        # Mock the data retriever to return empty dataframe
        with patch('api.enhanced_audience_api.data_retriever.fetch_data') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame()
            
            # Test confirm action
            response = self.client.post('/api/nl/process',
                                       json={
                                           'session_id': session_id,
                                           'action': 'confirm',
                                           'payload': {
                                               'confirmed_variables': ['VAR1', 'VAR2']
                                           }
                                       },
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'No data available for selected variables')
            
    def test_analyze_group_characteristics_handles_empty_data(self):
        """Test that analyze_group_characteristics handles edge cases"""
        # Test with empty dataframe
        empty_df = pd.DataFrame()
        result = analyze_group_characteristics(empty_df)
        self.assertEqual(result, {})
        
        # Test with only Group column
        group_only_df = pd.DataFrame({'Group': [0, 0, 1, 1]})
        result = analyze_group_characteristics(group_only_df)
        self.assertEqual(result, {})
        
    def test_analyze_group_characteristics_mixed_types(self):
        """Test analyze_group_characteristics with mixed data types"""
        test_df = pd.DataFrame({
            'Group': [0, 0, 0],
            'categorical': ['A', 'A', 'B'],
            'numeric': [1.5, 2.5, 3.5],
            'boolean': [True, False, True]
        })
        
        result = analyze_group_characteristics(test_df)
        
        # Check categorical handling
        self.assertIn('categorical', result)
        self.assertEqual(result['categorical']['dominant_value'], 'A')
        self.assertAlmostEqual(result['categorical']['dominant_percentage'], 66.7, places=1)
        
        # Check numeric handling
        self.assertIn('numeric', result)
        self.assertAlmostEqual(result['numeric']['median'], 2.5)
        self.assertAlmostEqual(result['numeric']['mean'], 2.5)
        
    def test_clustering_with_size_constraints(self):
        """Test that clustering respects size constraints even with edge cases"""
        clusterer = ConstrainedKMedians(min_size_pct=0.05, max_size_pct=0.10)
        
        # Test with minimum viable data (100 records for 5% = 5 records per cluster min)
        test_data = pd.DataFrame({
            'var1': np.random.randn(100),
            'var2': np.random.choice(['A', 'B', 'C'], 100),
            'var3': np.random.randint(0, 10, 100)
        })
        
        labels = clusterer.fit_predict(test_data)
        
        # Check that all constraints are satisfied
        unique_labels, counts = np.unique(labels, return_counts=True)
        for count in counts:
            self.assertGreaterEqual(count, 5)  # 5% of 100
            self.assertLessEqual(count, 10)     # 10% of 100
            
    def test_navigation_route_exists(self):
        """Test that distribution route is properly configured"""
        # This would be a frontend test, but we can verify the API accepts distribution requests
        response = self.client.post('/api/distribute',
                                   json={
                                       'audience_id': 'test-id',
                                       'platforms': ['facebook', 'google']
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data)


class TestErrorHandling(unittest.TestCase):
    """Test error handling improvements"""
    
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        sessions.clear()
        
    def test_invalid_session_handling(self):
        """Test that invalid session IDs are handled gracefully"""
        response = self.client.post('/api/nl/process',
                                   json={
                                       'session_id': 'invalid-session-id',
                                       'action': 'process',
                                       'payload': {'input': 'test'}
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid session')
        
    def test_exception_handling_in_process(self):
        """Test that exceptions in processing are caught and returned as errors"""
        # Start a session
        response = self.client.post('/api/nl/start_session',
                                   content_type='application/json')
        session_data = json.loads(response.data)
        session_id = session_data['session_id']
        
        # Mock variable selector to raise an exception
        with patch('api.enhanced_audience_api.variable_selector.analyze_request') as mock_analyze:
            mock_analyze.side_effect = Exception("Test exception")
            
            response = self.client.post('/api/nl/process',
                                       json={
                                           'session_id': session_id,
                                           'action': 'process',
                                           'payload': {'input': 'test query'}
                                       },
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'Test exception')
            
    def test_data_type_persistence(self):
        """Test that data type and subtype are properly stored in session"""
        # Start a session
        response = self.client.post('/api/nl/start_session',
                                   content_type='application/json')
        session_data = json.loads(response.data)
        session_id = session_data['session_id']
        
        # Send a process request with data type
        response = self.client.post('/api/nl/process',
                                   json={
                                       'session_id': session_id,
                                       'action': 'process',
                                       'payload': {
                                           'input': 'test query',
                                           'data_type': 'first_party',
                                           'subtype': 'rampid'
                                       }
                                   },
                                   content_type='application/json')
        
        # Verify data type is stored
        self.assertIn(session_id, sessions)
        self.assertEqual(sessions[session_id].data_type, 'first_party')
        self.assertEqual(sessions[session_id].subtype, 'rampid')


if __name__ == '__main__':
    unittest.main()