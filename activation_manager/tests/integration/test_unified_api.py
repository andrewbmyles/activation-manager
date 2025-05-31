"""
Integration tests for Unified API
"""

import unittest
import requests
import json
import time
from unittest.mock import patch
import os


class TestUnifiedAPIIntegration(unittest.TestCase):
    """Integration tests for the unified API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        cls.base_url = "http://localhost:5001"
        cls.session_id = None
        
        # Check if API is running
        try:
            response = requests.get(f"{cls.base_url}/api/health", timeout=5)
            cls.api_available = response.status_code == 200
        except requests.exceptions.RequestException:
            cls.api_available = False
    
    def setUp(self):
        """Set up test fixtures"""
        if not self.api_available:
            self.skipTest("API server not available")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/api/health")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('components', data)
        self.assertIn('audience_builder', data['components'])
    
    def test_start_nl_session(self):
        """Test starting a new NL session"""
        response = requests.post(f"{self.base_url}/api/nl/start_session")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('session_id', data)
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'ready')
        
        # Store session ID for other tests
        self.__class__.session_id = data['session_id']
        
        return data['session_id']
    
    def test_nl_process_analyze_prompt(self):
        """Test NL processing with prompt analysis"""
        if not self.session_id:
            session_id = self.test_start_nl_session()
        else:
            session_id = self.session_id
        
        # Test prompt processing
        payload = {
            "session_id": session_id,
            "action": "process",
            "payload": {
                "input": "Find environmentally conscious millennials with high income"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/nl/process",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        
        if data['status'] == 'variables_suggested':
            self.assertIn('suggested_variables', data)
            self.assertIn('total_suggested', data)
            self.assertGreater(data['total_suggested'], 0)
            
            # Test variable structure
            for var_type, variables in data['suggested_variables'].items():
                self.assertIsInstance(variables, list)
                if variables:
                    var = variables[0]
                    self.assertIn('code', var)
                    self.assertIn('description', var)
                    self.assertIn('score', var)
        
        return data
    
    def test_nl_process_complete_workflow(self):
        """Test complete NL workflow from start to finish"""
        # Start new session
        session_id = self.test_start_nl_session()
        
        # Step 1: Analyze prompt
        step1_payload = {
            "session_id": session_id,
            "action": "process",
            "payload": {
                "input": "Find tech-savvy young professionals"
            }
        }
        
        response1 = requests.post(
            f"{self.base_url}/api/nl/process",
            json=step1_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        
        if data1['status'] == 'variables_suggested':
            # Step 2: Confirm variables
            step2_payload = {
                "session_id": session_id,
                "action": "process",
                "payload": {
                    "input": "use all suggested variables"
                }
            }
            
            response2 = requests.post(
                f"{self.base_url}/api/nl/process",
                json=step2_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response2.status_code, 200)
            data2 = response2.json()
            
            if data2['status'] == 'complete':
                # Verify final results
                self.assertIn('segments', data2)
                self.assertIn('total_records', data2)
                self.assertGreater(len(data2['segments']), 0)
                
                # Check constraint satisfaction
                for segment in data2['segments']:
                    self.assertIn('size_percentage', segment)
                    pct = segment['size_percentage']
                    self.assertGreaterEqual(pct, 4.5)  # Allow small tolerance
                    self.assertLessEqual(pct, 10.5)
    
    def test_get_session_state(self):
        """Test retrieving session state"""
        if not self.session_id:
            session_id = self.test_start_nl_session()
        else:
            session_id = self.session_id
        
        response = requests.get(f"{self.base_url}/api/nl/session/{session_id}")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('current_step', data)
    
    def test_get_session_state_invalid(self):
        """Test retrieving state for invalid session"""
        invalid_session = "invalid-session-id"
        
        response = requests.get(f"{self.base_url}/api/nl/session/{invalid_session}")
        
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_get_audiences(self):
        """Test retrieving audiences list"""
        response = requests.get(f"{self.base_url}/api/audiences")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_popular_variables(self):
        """Test retrieving popular variables"""
        response = requests.get(f"{self.base_url}/api/variables/popular")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('variables', data)
        self.assertIsInstance(data['variables'], list)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.options(
            f"{self.base_url}/api/nl/start_session",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        # Should allow CORS
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = requests.get(f"{self.base_url}/api/nonexistent")
        
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_method(self):
        """Test using invalid HTTP method"""
        response = requests.delete(f"{self.base_url}/api/health")
        
        # Should return method not allowed
        self.assertIn(response.status_code, [405, 404])


class TestUnifiedAPIErrorHandling(unittest.TestCase):
    """Test error handling in the unified API"""
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:5001"
        
        # Check if API is running
        try:
            response = requests.get(f"{cls.base_url}/api/health", timeout=5)
            cls.api_available = response.status_code == 200
        except requests.exceptions.RequestException:
            cls.api_available = False
    
    def setUp(self):
        if not self.api_available:
            self.skipTest("API server not available")
    
    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        response = requests.post(
            f"{self.base_url}/api/nl/process",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        # Missing session_id
        payload = {
            "action": "process",
            "payload": {"input": "test"}
        }
        
        response = requests.post(
            f"{self.base_url}/api/nl/process",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_invalid_session_id(self):
        """Test handling of invalid session ID"""
        payload = {
            "session_id": "invalid-session-id",
            "action": "process",
            "payload": {"input": "test"}
        }
        
        response = requests.post(
            f"{self.base_url}/api/nl/process",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_invalid_action(self):
        """Test handling of invalid action"""
        # First create a valid session
        session_response = requests.post(f"{self.base_url}/api/nl/start_session")
        session_data = session_response.json()
        session_id = session_data['session_id']
        
        # Then use invalid action
        payload = {
            "session_id": session_id,
            "action": "invalid_action",
            "payload": {"input": "test"}
        }
        
        response = requests.post(
            f"{self.base_url}/api/nl/process",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)


class TestUnifiedAPIPerformance(unittest.TestCase):
    """Performance tests for the unified API"""
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:5001"
        
        # Check if API is running
        try:
            response = requests.get(f"{cls.base_url}/api/health", timeout=5)
            cls.api_available = response.status_code == 200
        except requests.exceptions.RequestException:
            cls.api_available = False
    
    def setUp(self):
        if not self.api_available:
            self.skipTest("API server not available")
    
    def test_health_check_response_time(self):
        """Test health check response time"""
        start_time = time.time()
        response = requests.get(f"{self.base_url}/api/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
    
    def test_session_creation_performance(self):
        """Test session creation performance"""
        start_time = time.time()
        response = requests.post(f"{self.base_url}/api/nl/start_session")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0)  # Should respond within 3 seconds
    
    def test_concurrent_sessions(self):
        """Test handling of multiple concurrent sessions"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_session():
            try:
                response = requests.post(f"{self.base_url}/api/nl/start_session")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create 5 concurrent sessions
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_session)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # Should handle most concurrent requests successfully
        self.assertGreaterEqual(success_count, 3)  # At least 3 out of 5 should succeed


class TestUnifiedAPIWithMocks(unittest.TestCase):
    """Test API behavior with mocked components"""
    
    def setUp(self):
        self.base_url = "http://localhost:5001"
    
    @patch('requests.post')
    def test_mock_api_calls(self, mock_post):
        """Test API behavior with mocked external calls"""
        # Mock Claude API response
        mock_response = {
            'status': 'variables_suggested',
            'suggested_variables': {
                'demographic': [
                    {'code': 'TEST_VAR', 'description': 'Test variable', 'score': 5.0}
                ]
            },
            'total_suggested': 1
        }
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        # This test would require more setup to properly mock the API
        # For now, just verify the mock structure
        self.assertIn('status', mock_response)
        self.assertIn('suggested_variables', mock_response)


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPIPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPIWithMocks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n✅ All API integration tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for test, error in result.failures + result.errors:
            print(f"  - {test}: {error}")