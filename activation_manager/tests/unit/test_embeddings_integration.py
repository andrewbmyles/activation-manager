"""
Unit tests for embeddings integration
"""

import unittest
import os
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Import the modules to test
from activation_manager.core.embeddings_handler import EmbeddingsHandler, EmbeddingsCache
from activation_manager.core.variable_selector import VariableSelector
from activation_manager.utils.embeddings_loader import EmbeddingsLoader


class TestEmbeddingsCache(unittest.TestCase):
    """Test the embeddings cache functionality"""
    
    def setUp(self):
        self.cache = EmbeddingsCache(cache_size=3)
    
    def test_cache_basic_operations(self):
        """Test basic cache get/set operations"""
        # Test set and get
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Test missing key
        self.assertIsNone(self.cache.get("missing_key"))
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        # Fill cache
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        self.cache.get("key1")
        
        # Add new item, should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        self.assertIsNone(self.cache.get("key2"))
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get("key4"), "value4")


class TestEmbeddingsHandler(unittest.TestCase):
    """Test the embeddings handler functionality"""
    
    def setUp(self):
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock embeddings data
        self.embeddings_data = pd.DataFrame({
            'varid': ['VAR1', 'VAR2', 'VAR3'],
            'embedding': [
                np.random.rand(1536).tolist(),
                np.random.rand(1536).tolist(),
                np.random.rand(1536).tolist()
            ]
        })
        
        self.embeddings_path = os.path.join(self.temp_dir, 'embeddings.parquet')
        self.embeddings_data.to_parquet(self.embeddings_path)
        
        # Create mock enriched data
        self.enriched_path = os.path.join(self.temp_dir, 'enriched.jsonl')
        with open(self.enriched_path, 'w') as f:
            f.write(json.dumps({'varid': 'VAR1', 'description': 'Variable 1 description'}) + '\n')
            f.write(json.dumps({'varid': 'VAR2', 'description': 'Variable 2 description'}) + '\n')
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_embeddings_loading(self):
        """Test loading embeddings from parquet file"""
        handler = EmbeddingsHandler(self.embeddings_path)
        
        self.assertEqual(len(handler.variable_ids), 3)
        self.assertEqual(handler.variable_ids, ['VAR1', 'VAR2', 'VAR3'])
        self.assertEqual(handler.embeddings_matrix.shape, (3, 1536))
    
    def test_faiss_index_creation(self):
        """Test FAISS index is created correctly"""
        handler = EmbeddingsHandler(self.embeddings_path)
        
        self.assertIsNotNone(handler.index)
        self.assertEqual(handler.index.ntotal, 3)
    
    def test_enriched_data_loading(self):
        """Test loading enriched data from JSONL"""
        handler = EmbeddingsHandler(self.embeddings_path, self.enriched_path)
        
        self.assertEqual(len(handler.enriched_data), 2)
        self.assertEqual(handler.get_variable_info('VAR1')['description'], 'Variable 1 description')
    
    def test_similarity_search(self):
        """Test similarity search functionality"""
        handler = EmbeddingsHandler(self.embeddings_path)
        
        # Create a query embedding (use first variable's embedding as query)
        query_embedding = handler.get_variable_embedding('VAR1')
        
        results = handler.search_similar_variables(query_embedding, k=2)
        
        self.assertEqual(len(results), 2)
        # First result should be VAR1 itself with highest similarity
        self.assertEqual(results[0][0], 'VAR1')
        self.assertGreater(results[0][1], 0.9)  # Should be close to 1.0
    
    def test_find_similar_by_variable(self):
        """Test finding similar variables by variable ID"""
        handler = EmbeddingsHandler(self.embeddings_path)
        
        results = handler.find_similar_by_variable('VAR1', k=2)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], 'VAR1')


class TestEmbeddingsLoader(unittest.TestCase):
    """Test the embeddings loader utility"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = tempfile.mkdtemp()
        
        # Create mock source files
        self.mock_embeddings = pd.DataFrame({
            'varid': ['TEST1'],
            'embedding': [np.random.rand(1536).tolist()]
        })
        self.mock_embeddings.to_parquet(os.path.join(self.source_dir, 'variable_vectors_enhanced.parquet'))
        
        with open(os.path.join(self.source_dir, 'variable_catalogue_enhanced.jsonl'), 'w') as f:
            f.write(json.dumps({'varid': 'TEST1', 'description': 'Test variable'}) + '\n')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.source_dir)
    
    def test_setup_embeddings(self):
        """Test copying embeddings files to project"""
        result = EmbeddingsLoader.setup_embeddings(self.source_dir, self.temp_dir)
        
        self.assertIn('embeddings', result)
        self.assertIn('enriched_data', result)
        self.assertIn('config', result)
        
        # Check files were copied
        self.assertTrue(os.path.exists(result['embeddings']))
        self.assertTrue(os.path.exists(result['config']))
    
    def test_verify_embeddings(self):
        """Test embeddings verification"""
        # Setup embeddings first
        EmbeddingsLoader.setup_embeddings(self.source_dir, self.temp_dir)
        
        # Mock the config loading to point to our temp dir
        with patch.object(EmbeddingsLoader, 'get_embeddings_config') as mock_config:
            mock_config.return_value = {
                'embeddings_path': os.path.join(self.temp_dir, 'variable_vectors_enhanced.parquet'),
                'enriched_data_path': os.path.join(self.temp_dir, 'variable_catalogue_enhanced.jsonl')
            }
            
            self.assertTrue(EmbeddingsLoader.verify_embeddings())


class TestVariableSelector(unittest.TestCase):
    """Test the enhanced variable selector with embeddings"""
    
    @patch('activation_manager.core.variable_selector.EmbeddingsHandler')
    def test_embeddings_initialization(self, mock_handler):
        """Test that embeddings are initialized when available"""
        # Mock the embeddings handler
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance
        
        with patch('activation_manager.core.variable_selector.EMBEDDINGS_AVAILABLE', True):
            with patch('activation_manager.core.variable_selector.LOADER_AVAILABLE', True):
                with patch('activation_manager.core.variable_selector.EmbeddingsLoader') as mock_loader:
                    mock_loader.get_embeddings_config.return_value = {
                        'embeddings_path': '/fake/path/embeddings.parquet',
                        'enriched_data_path': '/fake/path/enriched.jsonl'
                    }
                    
                    selector = VariableSelector(use_embeddings=True)
                    
                    self.assertTrue(selector.use_embeddings)
                    self.assertIsNotNone(selector.embeddings_handler)
    
    def test_fallback_to_tfidf(self):
        """Test fallback to TF-IDF when embeddings unavailable"""
        with patch('activation_manager.core.variable_selector.EMBEDDINGS_AVAILABLE', False):
            selector = VariableSelector(use_embeddings=True)
            
            self.assertFalse(selector.use_embeddings)
            self.assertIsNone(selector.embeddings_handler)
    
    @patch('activation_manager.core.variable_selector.EmbeddingsHandler')
    def test_analyze_request_with_embeddings(self, mock_handler):
        """Test analyze_request uses embeddings when available"""
        # Setup mock embeddings handler
        mock_instance = MagicMock()
        mock_instance.find_similar_by_variable.return_value = [
            ('VAR1', 0.95),
            ('VAR2', 0.85)
        ]
        mock_instance.get_variable_info.return_value = {'extra': 'info'}
        mock_handler.return_value = mock_instance
        
        with patch('activation_manager.core.variable_selector.EMBEDDINGS_AVAILABLE', True):
            selector = VariableSelector(use_embeddings=True)
            selector.embeddings_handler = mock_instance
            
            # Mock the dataframe
            selector.variables_df = pd.DataFrame({
                'code': ['VAR1', 'VAR2'],
                'description': ['Variable 1', 'Variable 2'],
                'category': ['Cat1', 'Cat2'],
                'type': ['demographic', 'behavioral'],
                'source': ['source1', 'source2'],
                'enhanced_description': ['Enhanced desc 1', 'Enhanced desc 2']
            })
            
            results = selector.analyze_request("test query", top_n=2)
            
            # Check that embeddings were used
            mock_instance.find_similar_by_variable.assert_called()
            
            # Check results include enriched info
            self.assertEqual(len(results), 2)
            self.assertIn('enriched_info', results[0])


if __name__ == '__main__':
    unittest.main()