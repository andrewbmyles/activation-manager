#!/usr/bin/env python3
"""
Unit tests for data persistence functionality
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_persistence.parquet_handlers_fixed import (
    AudienceHandler, PlatformHandler, DistributionHandler
)


class TestAudienceHandler(unittest.TestCase):
    """Test cases for AudienceHandler"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = AudienceHandler(base_path=self.temp_dir)
        
        # Sample audience data
        self.sample_audience = {
            'user_id': 'test_user',
            'name': 'Test Audience',
            'description': 'Test audience for unit tests',
            'data_type': 'first_party',
            'original_query': 'test query',
            'selected_variables': ['VAR1', 'VAR2', 'VAR3'],
            'variable_details': [
                {
                    'code': 'VAR1',
                    'description': 'Variable 1',
                    'relevance_score': 0.95,
                    'type': 'demographic',
                    'category': 'Demographics'
                },
                {
                    'code': 'VAR2',
                    'description': 'Variable 2',
                    'relevance_score': 0.85,
                    'type': 'behavioral',
                    'category': 'Behavioral'
                }
            ],
            'segments': [
                {
                    'segment_id': 0,
                    'name': 'Segment 1',
                    'size': 50000,
                    'size_percentage': 5.0,
                    'characteristics': {'key': 'value'},
                    'prizm_segments': ['PRIZM1']
                }
            ],
            'total_audience_size': 50000,
            'status': 'active',
            'metadata': {
                'created_from': 'unit_test',
                'session_id': 'test_session'
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_audience(self):
        """Test saving an audience"""
        audience_id = self.handler.save_audience(self.sample_audience)
        
        # Check that ID was returned
        self.assertIsNotNone(audience_id)
        self.assertTrue(audience_id.startswith('aud_'))
        
        # Check that file was created
        user_path = Path(self.temp_dir) / 'audiences' / 'user_id=test_user'
        self.assertTrue(user_path.exists())
        
        # Check partitioned structure
        now = datetime.now()
        file_path = user_path / f'year={now.year}' / f'month={now.month:02d}' / f'audiences_{now.year}{now.month:02d}.parquet'
        self.assertTrue(file_path.exists())
    
    def test_get_audience(self):
        """Test retrieving a saved audience"""
        # Save audience first
        audience_id = self.handler.save_audience(self.sample_audience)
        
        # Retrieve it
        retrieved = self.handler.get_audience(audience_id, 'test_user')
        
        # Verify data
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['audience_id'], audience_id)
        self.assertEqual(retrieved['name'], 'Test Audience')
        self.assertEqual(retrieved['description'], 'Test audience for unit tests')
        self.assertEqual(len(retrieved['selected_variables']), 3)
        self.assertEqual(retrieved['total_audience_size'], 50000)
    
    def test_get_nonexistent_audience(self):
        """Test retrieving a non-existent audience"""
        result = self.handler.get_audience('fake_id', 'test_user')
        self.assertIsNone(result)
    
    def test_list_audiences(self):
        """Test listing audiences for a user"""
        # Save multiple audiences
        ids = []
        for i in range(3):
            audience = self.sample_audience.copy()
            audience['name'] = f'Test Audience {i+1}'
            audience_id = self.handler.save_audience(audience)
            ids.append(audience_id)
        
        # List audiences
        audiences = self.handler.list_audiences('test_user')
        
        # Verify
        self.assertEqual(len(audiences), 3)
        # Should be sorted by created_at descending (newest first)
        self.assertEqual(audiences[0]['name'], 'Test Audience 3')
        self.assertEqual(audiences[1]['name'], 'Test Audience 2')
        self.assertEqual(audiences[2]['name'], 'Test Audience 1')
    
    def test_list_audiences_with_status_filter(self):
        """Test listing audiences with status filter"""
        # Save audiences with different statuses
        active_audience = self.sample_audience.copy()
        active_audience['name'] = 'Active Audience'
        active_audience['status'] = 'active'
        active_id = self.handler.save_audience(active_audience)
        
        archived_audience = self.sample_audience.copy()
        archived_audience['name'] = 'Archived Audience'
        archived_audience['status'] = 'archived'
        archived_id = self.handler.save_audience(archived_audience)
        
        # List only active audiences
        active_audiences = self.handler.list_audiences('test_user', status='active')
        self.assertEqual(len(active_audiences), 1)
        self.assertEqual(active_audiences[0]['name'], 'Active Audience')
        
        # List only archived audiences
        archived_audiences = self.handler.list_audiences('test_user', status='archived')
        self.assertEqual(len(archived_audiences), 1)
        self.assertEqual(archived_audiences[0]['name'], 'Archived Audience')
    
    def test_update_audience_status(self):
        """Test updating audience status"""
        # Save audience
        audience_id = self.handler.save_audience(self.sample_audience)
        
        # Update status to archived
        success = self.handler.update_audience_status(audience_id, 'test_user', 'archived')
        self.assertTrue(success)
        
        # Verify status was updated
        audience = self.handler.get_audience(audience_id, 'test_user')
        self.assertEqual(audience['status'], 'archived')
        self.assertIsNotNone(audience['updated_at'])
    
    def test_update_nonexistent_audience_status(self):
        """Test updating status of non-existent audience"""
        success = self.handler.update_audience_status('fake_id', 'test_user', 'archived')
        self.assertFalse(success)
    
    def test_cross_user_isolation(self):
        """Test that users cannot access each other's audiences"""
        # Save audience for user1
        audience_id = self.handler.save_audience(self.sample_audience)
        
        # Try to access from user2
        result = self.handler.get_audience(audience_id, 'different_user')
        self.assertIsNone(result)
        
        # List should be empty for user2
        audiences = self.handler.list_audiences('different_user')
        self.assertEqual(len(audiences), 0)


class TestPlatformHandler(unittest.TestCase):
    """Test cases for PlatformHandler"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = PlatformHandler(base_path=self.temp_dir)
        
        # Sample platform data
        self.sample_platform = {
            'user_id': 'test_user',
            'platform_type': 'the_trade_desk',
            'name': 'Test TTD Account',
            'credentials': {
                'encrypted': 'encrypted_api_key_here',
                'account_id': '12345'
            },
            'settings': {
                'default_match_rate': 0.7,
                'auto_refresh': True,
                'refresh_frequency': 'weekly'
            },
            'status': 'connected'
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_platform(self):
        """Test saving a platform configuration"""
        platform_id = self.handler.save_platform(self.sample_platform)
        
        # Check that ID was returned
        self.assertIsNotNone(platform_id)
        self.assertTrue(platform_id.startswith('plat_'))
        
        # Check that file was created
        file_path = Path(self.temp_dir) / 'platforms' / 'user_id=test_user' / 'platforms.parquet'
        self.assertTrue(file_path.exists())
    
    def test_get_platform(self):
        """Test retrieving a saved platform"""
        # Save platform first
        platform_id = self.handler.save_platform(self.sample_platform)
        
        # Retrieve it
        retrieved = self.handler.get_platform(platform_id, 'test_user')
        
        # Verify data
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['platform_id'], platform_id)
        self.assertEqual(retrieved['name'], 'Test TTD Account')
        self.assertEqual(retrieved['platform_type'], 'the_trade_desk')
        self.assertIn('encrypted', retrieved['credentials'])
    
    def test_list_platforms(self):
        """Test listing platforms for a user"""
        # Save multiple platforms
        platforms_data = [
            {'name': 'TTD Account', 'platform_type': 'the_trade_desk'},
            {'name': 'Meta Account', 'platform_type': 'meta'},
            {'name': 'Google Account', 'platform_type': 'google_ads'}
        ]
        
        for platform_data in platforms_data:
            platform = self.sample_platform.copy()
            platform.update(platform_data)
            self.handler.save_platform(platform)
        
        # List platforms
        platforms = self.handler.list_platforms('test_user')
        
        # Verify
        self.assertEqual(len(platforms), 3)
        platform_types = [p['platform_type'] for p in platforms]
        self.assertIn('the_trade_desk', platform_types)
        self.assertIn('meta', platform_types)
        self.assertIn('google_ads', platform_types)
    
    def test_update_platform_status(self):
        """Test updating platform status"""
        # Save platform
        platform_id = self.handler.save_platform(self.sample_platform)
        
        # Disconnect platform
        success = self.handler.update_platform_status(platform_id, 'test_user', 'disconnected')
        self.assertTrue(success)
        
        # Verify status was updated
        platform = self.handler.get_platform(platform_id, 'test_user')
        self.assertEqual(platform['status'], 'disconnected')


class TestDistributionHandler(unittest.TestCase):
    """Test cases for DistributionHandler"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = DistributionHandler(base_path=self.temp_dir)
        
        # Sample distribution data
        self.sample_distribution = {
            'user_id': 'test_user',
            'audience_id': 'aud_12345',
            'platform_id': 'plat_67890',
            'audience_name': 'Test Audience',
            'platform_name': 'Test Platform',
            'platform_type': 'the_trade_desk',
            'scheduled_at': datetime.now().isoformat(),
            'segments_distributed': [0, 1, 2],
            'total_records': 150000,
            'status': 'pending',
            'metadata': {
                'campaign_name': 'Test Campaign',
                'approval_status': 'pending'
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_distribution(self):
        """Test saving a distribution record"""
        distribution_id = self.handler.save_distribution(self.sample_distribution)
        
        # Check that ID was returned
        self.assertIsNotNone(distribution_id)
        self.assertTrue(distribution_id.startswith('dist_'))
        
        # Check that file was created with partitioning
        now = datetime.now()
        file_path = (Path(self.temp_dir) / 'distributions' / 'user_id=test_user' / 
                    f'year={now.year}' / f'month={now.month:02d}' / 
                    f'distributions_{now.year}{now.month:02d}.parquet')
        self.assertTrue(file_path.exists())
    
    def test_get_distribution(self):
        """Test retrieving a saved distribution"""
        # Save distribution first
        distribution_id = self.handler.save_distribution(self.sample_distribution)
        
        # Retrieve it
        retrieved = self.handler.get_distribution(distribution_id, 'test_user')
        
        # Verify data
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['distribution_id'], distribution_id)
        self.assertEqual(retrieved['audience_name'], 'Test Audience')
        self.assertEqual(retrieved['total_records'], 150000)
        self.assertEqual(len(retrieved['segments_distributed']), 3)
    
    def test_list_distributions(self):
        """Test listing distributions"""
        # Save multiple distributions
        for i in range(3):
            distribution = self.sample_distribution.copy()
            distribution['audience_name'] = f'Audience {i+1}'
            self.handler.save_distribution(distribution)
        
        # List distributions
        distributions = self.handler.list_distributions('test_user')
        
        # Verify
        self.assertEqual(len(distributions), 3)
    
    def test_update_distribution_status(self):
        """Test updating distribution status flow"""
        # Save distribution
        distribution_id = self.handler.save_distribution(self.sample_distribution)
        
        # Update to in_progress
        result = self.handler.update_distribution_status(
            distribution_id, 'test_user', 'in_progress',
            metadata={'started_at': datetime.now().isoformat()}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'in_progress')
        
        # Update to completed with match rate
        result = self.handler.update_distribution_status(
            distribution_id, 'test_user', 'completed',
            metadata={
                'completed_at': datetime.now().isoformat(),
                'match_rate': 0.72,
                'matched_records': 108000
            }
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['metadata']['match_rate'], 0.72)


class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.audience_handler = AudienceHandler(base_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        # Audience without user_id
        invalid_audience = {
            'name': 'Test Audience',
            'data_type': 'first_party',
            'selected_variables': ['VAR1']
        }
        
        with self.assertRaises(KeyError):
            self.audience_handler.save_audience(invalid_audience)
    
    def test_empty_variables(self):
        """Test handling of empty variables list"""
        audience = {
            'user_id': 'test_user',
            'name': 'Test Audience',
            'data_type': 'first_party',
            'selected_variables': [],  # Empty list
            'status': 'active'
        }
        
        # Should still save successfully
        audience_id = self.audience_handler.save_audience(audience)
        self.assertIsNotNone(audience_id)
        
        # Verify it saved with empty variables
        retrieved = self.audience_handler.get_audience(audience_id, 'test_user')
        self.assertEqual(len(retrieved['selected_variables']), 0)


class TestConcurrency(unittest.TestCase):
    """Test concurrent access scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = AudienceHandler(base_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_concurrent_saves(self):
        """Test saving multiple audiences concurrently"""
        import threading
        
        audience_ids = []
        errors = []
        
        def save_audience(index):
            try:
                audience = {
                    'user_id': 'test_user',
                    'name': f'Concurrent Audience {index}',
                    'data_type': 'first_party',
                    'selected_variables': [f'VAR{index}'],
                    'status': 'active'
                }
                audience_id = self.handler.save_audience(audience)
                audience_ids.append(audience_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_audience, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(audience_ids), 5)
        self.assertEqual(len(set(audience_ids)), 5, "Duplicate IDs generated")
        
        # Verify all audiences were saved
        audiences = self.handler.list_audiences('test_user')
        self.assertEqual(len(audiences), 5)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)