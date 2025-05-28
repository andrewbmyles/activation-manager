"""
Unit tests for IntegratedAudienceHandler
"""

import unittest
import asyncio
import tempfile
import os
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
from integrated_audience_handler import IntegratedAudienceHandler, WorkflowState


class TestWorkflowState(unittest.TestCase):
    """Test the WorkflowState class"""
    
    def test_initialization(self):
        """Test WorkflowState initialization"""
        state = WorkflowState()
        
        self.assertEqual(state.current_step, "initial")
        self.assertEqual(state.user_prompt, "")
        self.assertEqual(state.parsed_requirements, {})
        self.assertEqual(state.suggested_variables, [])
        self.assertEqual(state.confirmed_variables, [])
        self.assertIsNone(state.data)
        self.assertEqual(state.segments, [])


class TestIntegratedAudienceHandler(unittest.TestCase):
    """Test the IntegratedAudienceHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary data file
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_path = os.path.join(self.temp_dir, 'test_data.csv')
        
        # Create test data
        np.random.seed(42)
        test_data = pd.DataFrame({
            'AGE_RANGE': np.random.choice(['18-24', '25-34', '35-44'], 100),
            'INCOME_LEVEL': np.random.choice(['Low', 'Medium', 'High'], 100),
            'LOCATION_TYPE': np.random.choice(['Urban', 'Suburban', 'Rural'], 100),
            'TECH_SCORE': np.random.randint(1, 11, 100),
            'PRIZM_CLUSTER': np.random.choice(['Young Digerati', 'Money & Brains', 'Kids & Cul-de-Sacs'], 100)
        })
        test_data.to_csv(self.test_data_path, index=False)
        
        # Initialize handler
        self.handler = IntegratedAudienceHandler(
            anthropic_api_key="test_key",
            data_path=self.test_data_path
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test handler initialization"""
        self.assertEqual(self.handler.anthropic_api_key, "test_key")
        self.assertIsNotNone(self.handler.variable_selector)
        self.assertIsNotNone(self.handler.data_retriever)
        self.assertIsNotNone(self.handler.clusterer)
        self.assertIsNotNone(self.handler.prizm_analyzer)
        self.assertEqual(self.handler.state.current_step, "initial")
    
    def test_fallback_parse(self):
        """Test fallback parsing functionality"""
        # Test demographic keywords
        result = self.handler._fallback_parse("young millennials in urban areas")
        self.assertIn("age groups", result["demographic"])
        self.assertIn("location type", result["demographic"])
        
        # Test financial keywords
        result = self.handler._fallback_parse("high income affluent customers")
        self.assertIn("income level", result["financial"])
        
        # Test behavioral keywords
        result = self.handler._fallback_parse("frequent buyers who purchase online")
        self.assertIn("purchase behavior", result["behavioral"])
        
        # Test psychographic keywords
        result = self.handler._fallback_parse("environmentally conscious lifestyle")
        self.assertIn("lifestyle values", result["psychographic"])
    
    @patch('aiohttp.ClientSession.post')
    async def test_parse_with_claude_success(self, mock_post):
        """Test successful Claude API parsing"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "content": [{"text": "Parsed requirements"}]
        })
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await self.handler._parse_with_claude("test prompt")
        
        # Should return structured requirements
        self.assertIn("demographic", result)
        self.assertIn("behavioral", result)
        self.assertIn("financial", result)
        self.assertIn("psychographic", result)
    
    @patch('aiohttp.ClientSession.post')
    async def test_parse_with_claude_failure(self, mock_post):
        """Test Claude API failure fallback"""
        # Mock API failure
        mock_post.side_effect = Exception("API Error")
        
        result = await self.handler._parse_with_claude("test prompt")
        
        # Should fallback to keyword parsing
        self.assertIn("demographic", result)
        self.assertIn("behavioral", result)
        self.assertIn("financial", result)
        self.assertIn("psychographic", result)
    
    async def test_analyze_prompt(self):
        """Test prompt analysis workflow"""
        prompt = "Find tech-savvy millennials with high income"
        
        result = await self.handler.analyze_prompt(prompt)
        
        self.assertEqual(result["status"], "variables_suggested")
        self.assertIn("suggested_variables", result)
        self.assertIn("total_suggested", result)
        self.assertGreater(result["total_suggested"], 0)
        
        # Check that state is updated
        self.assertEqual(self.handler.state.current_step, "awaiting_confirmation")
        self.assertEqual(self.handler.state.user_prompt, prompt)
    
    async def test_handle_variable_confirmation_all(self):
        """Test variable confirmation with 'all' response"""
        # First analyze a prompt to get variables
        await self.handler.analyze_prompt("test prompt")
        
        # Then confirm with "all"
        result = await self.handler.handle_variable_confirmation("use all suggested variables")
        
        self.assertEqual(result["status"], "complete")
        self.assertIn("segments", result)
        self.assertGreater(len(result["segments"]), 0)
    
    async def test_handle_variable_confirmation_specific(self):
        """Test variable confirmation with specific variables"""
        # First analyze a prompt
        await self.handler.analyze_prompt("income and age")
        
        # Get some variable codes
        if self.handler.state.suggested_variables:
            first_var_code = self.handler.state.suggested_variables[0]['code']
            response = f"use {first_var_code}"
            
            result = await self.handler.handle_variable_confirmation(response)
            
            # Should proceed with clustering
            self.assertEqual(result["status"], "complete")
    
    async def test_handle_variable_confirmation_no_match(self):
        """Test variable confirmation with no matching variables"""
        # First analyze a prompt
        await self.handler.analyze_prompt("test prompt")
        
        result = await self.handler.handle_variable_confirmation("xyz nonexistent variable")
        
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("didn't catch", result["message"])
    
    async def test_retrieve_and_cluster(self):
        """Test data retrieval and clustering"""
        # Set up confirmed variables
        self.handler.state.confirmed_variables = ['AGE_RANGE', 'INCOME_LEVEL']
        self.handler.state.current_step = "variables_confirmed"
        
        result = await self.handler.retrieve_and_cluster()
        
        self.assertEqual(result["status"], "complete")
        self.assertIn("segments", result)
        self.assertIn("total_records", result)
        self.assertIn("variables_used", result)
        
        # Check segments have proper structure
        segments = result["segments"]
        self.assertGreater(len(segments), 0)
        
        for segment in segments:
            self.assertIn("group_id", segment)
            self.assertIn("size", segment)
            self.assertIn("size_percentage", segment)
            self.assertIn("characteristics", segment)
    
    async def test_retrieve_and_cluster_empty_data(self):
        """Test handling of empty data during clustering"""
        # Mock empty data return
        with patch.object(self.handler.data_retriever, 'fetch_data', return_value=pd.DataFrame()):
            self.handler.state.confirmed_variables = ['NONEXISTENT_VAR']
            
            result = await self.handler.retrieve_and_cluster()
            
            self.assertEqual(result["status"], "error")
            self.assertIn("No data available", result["message"])
    
    def test_analyze_group_characteristics_categorical(self):
        """Test group characteristics analysis for categorical data"""
        test_group = pd.DataFrame({
            'Group': [0, 0, 0],
            'LOCATION': ['Urban', 'Urban', 'Suburban'],
            'EDUCATION': ['College', 'College', 'College']
        })
        
        characteristics = self.handler._analyze_group_characteristics(test_group)
        
        self.assertIn('LOCATION', characteristics)
        self.assertIn('EDUCATION', characteristics)
        
        # Check LOCATION characteristics
        location_char = characteristics['LOCATION']
        self.assertEqual(location_char['type'], 'categorical')
        self.assertEqual(location_char['dominant_value'], 'Urban')
        self.assertIn('distribution', location_char)
    
    def test_analyze_group_characteristics_numeric(self):
        """Test group characteristics analysis for numeric data"""
        test_group = pd.DataFrame({
            'Group': [0, 0, 0],
            'AGE': [25, 30, 35],
            'SCORE': [8.5, 9.0, 7.5]
        })
        
        characteristics = self.handler._analyze_group_characteristics(test_group)
        
        self.assertIn('AGE', characteristics)
        self.assertIn('SCORE', characteristics)
        
        # Check AGE characteristics
        age_char = characteristics['AGE']
        self.assertEqual(age_char['type'], 'numeric')
        self.assertEqual(age_char['mean'], 30.0)
        self.assertEqual(age_char['median'], 30.0)
    
    def test_export_results_csv(self):
        """Test CSV export functionality"""
        # Set up some test data
        self.handler.state.data = pd.DataFrame({
            'Group': [0, 1, 0, 1],
            'AGE': [25, 35, 30, 40]
        })
        
        result = self.handler.export_results('csv')
        
        self.assertIsInstance(result, str)
        self.assertIn('Group,AGE', result)  # CSV header
    
    def test_export_results_json(self):
        """Test JSON export functionality"""
        # Set up test segments
        self.handler.state.segments = [
            {"group_id": 0, "size": 50, "size_percentage": 50.0},
            {"group_id": 1, "size": 50, "size_percentage": 50.0}
        ]
        self.handler.state.confirmed_variables = ['AGE', 'INCOME']
        
        result = self.handler.export_results('json')
        
        self.assertIsInstance(result, str)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        self.assertIn('segments', parsed)
        self.assertIn('metadata', parsed)
    
    def test_export_results_no_data(self):
        """Test export with no data"""
        self.handler.state.data = None
        
        result = self.handler.export_results('csv')
        
        self.assertIn('error', result)
        self.assertIn('No results to export', result['error'])
    
    def test_export_results_invalid_format(self):
        """Test export with invalid format"""
        self.handler.state.data = pd.DataFrame({'test': [1, 2, 3]})
        
        result = self.handler.export_results('invalid_format')
        
        self.assertIn('error', result)
        self.assertIn('Unsupported format', result['error'])


class TestIntegratedAudienceHandlerIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        # Use the real synthetic data if available
        data_path = "/Users/myles/Documents/Activation Manager/Synthetic_Data/output/synthetic_consumer_data_1000_20250525_155201.csv"
        
        if os.path.exists(data_path):
            self.handler = IntegratedAudienceHandler(
                anthropic_api_key="test_key",
                data_path=data_path
            )
            self.has_real_data = True
        else:
            # Create minimal test data
            self.temp_dir = tempfile.mkdtemp()
            test_data_path = os.path.join(self.temp_dir, 'test_data.csv')
            
            test_data = pd.DataFrame({
                'AGE_RANGE': ['25-34'] * 50 + ['35-44'] * 50,
                'INCOME_LEVEL': ['High'] * 50 + ['Medium'] * 50,
            })
            test_data.to_csv(test_data_path, index=False)
            
            self.handler = IntegratedAudienceHandler(
                anthropic_api_key="test_key",
                data_path=test_data_path
            )
            self.has_real_data = False
    
    def tearDown(self):
        """Clean up integration test fixtures"""
        if not self.has_real_data:
            import shutil
            shutil.rmtree(self.temp_dir)
    
    async def test_complete_workflow(self):
        """Test complete workflow from prompt to results"""
        # Test the entire process
        prompt = "Find young professionals with high income"
        
        # Step 1: Process initial request
        result = await self.handler.process_request(prompt)
        
        self.assertEqual(result["status"], "variables_suggested")
        self.assertIn("suggested_variables", result)
        
        # Step 2: Confirm variables (simulate user confirming all)
        session_id = list(self.handler.sessions.keys())[0] if self.handler.sessions else None
        confirmation = "use all suggested variables"
        
        final_result = await self.handler.process_request(confirmation, session_id)
        
        if final_result["status"] == "complete":
            self.assertIn("segments", final_result)
            self.assertIn("total_records", final_result)
            self.assertGreater(len(final_result["segments"]), 0)
            
            # Verify constraint satisfaction
            for segment in final_result["segments"]:
                pct = segment["size_percentage"]
                self.assertGreaterEqual(pct, 4.5)  # Allow small tolerance
                self.assertLessEqual(pct, 10.5)
    
    async def test_session_management(self):
        """Test session management across requests"""
        # First request should create a session
        result1 = await self.handler.process_request("test prompt 1")
        self.assertEqual(len(self.handler.sessions), 1)
        
        # Second request with different session should create another
        result2 = await self.handler.process_request("test prompt 2", "different_session")
        self.assertEqual(len(self.handler.sessions), 2)
        
        # Using existing session should reuse it
        session_id = list(self.handler.sessions.keys())[0]
        result3 = await self.handler.process_request("follow up", session_id)
        self.assertEqual(len(self.handler.sessions), 2)


if __name__ == '__main__':
    # Run the async tests
    def run_async_test(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowState))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedAudienceHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedAudienceHandlerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Monkey patch to handle async tests
    original_run = unittest.TestCase.run
    
    def patched_run(self, result=None):
        for method_name in dir(self):
            if method_name.startswith('test_'):
                method = getattr(self, method_name)
                if asyncio.iscoroutinefunction(method):
                    setattr(self, method_name, lambda: run_async_test(method()))
        return original_run(self, result)
    
    unittest.TestCase.run = patched_run
    
    runner.run(suite)