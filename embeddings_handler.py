"""
Embeddings handler for semantic variable search.
Integrates pre-computed embeddings with FAISS for efficient similarity search.
"""

import os
import numpy as np
import pandas as pd
import pickle
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import faiss
import logging
from functools import lru_cache
import json

logger = logging.getLogger(__name__)


class EmbeddingsHandler:
    """Handles loading and searching variable embeddings using FAISS."""
    
    def __init__(self, embeddings_path: str, enriched_data_path: Optional[str] = None, build_index: bool = True):
        """
        Initialize the embeddings handler.
        
        Args:
            embeddings_path: Path to the parquet file containing variable embeddings
            enriched_data_path: Optional path to enriched variable data (JSONL)
            build_index: Whether to build FAISS index (can be slow for large datasets)
        """
        self.embeddings_path = embeddings_path
        self.enriched_data_path = enriched_data_path
        self.embeddings_df = None
        self.index = None
        self.variable_ids = []
        self.enriched_data = {}
        self.embedding_dim = 1536  # OpenAI ada-002 dimension
        
        self._load_embeddings()
        if build_index:
            self._build_index()
        else:
            logger.info("Skipping FAISS index build for faster startup")
        if enriched_data_path:
            self._load_enriched_data()
    
    def _load_embeddings(self):
        """Load embeddings from numpy file or parquet."""
        try:
            logger.info(f"Loading embeddings from {self.embeddings_path}")
            
            # Check if embeddings_path is a directory
            embeddings_dir = Path(self.embeddings_path)
            if embeddings_dir.is_dir():
                # Look for numpy file
                npy_file = embeddings_dir / "variable_embeddings_full.npy"
                ids_file = embeddings_dir / "variable_ids_full.json"
                
                if npy_file.exists() and ids_file.exists():
                    # Load numpy embeddings
                    embeddings = np.load(npy_file)
                    with open(ids_file, 'r') as f:
                        variable_ids = json.load(f)
                    
                    # Create DataFrame
                    self.embeddings_df = pd.DataFrame({
                        'varid': variable_ids,
                        'embedding': list(embeddings)
                    })
                    
                    # Set up the embeddings matrix and variable IDs
                    self.variable_ids = variable_ids
                    self.embeddings_matrix = embeddings.astype(np.float32)
                    
                    logger.info(f"✅ Loaded {len(self.embeddings_df)} embeddings from numpy files")
                    return
            
            # Try loading as parquet file
            if str(self.embeddings_path).endswith('.parquet'):
                self.embeddings_df = pd.read_parquet(self.embeddings_path)
            
            # Extract variable IDs and embeddings
            self.variable_ids = self.embeddings_df['varid'].tolist()
            
            # Convert embeddings to numpy array
            embeddings_list = []
            for embedding in self.embeddings_df['embedding']:
                if isinstance(embedding, str):
                    # Parse string representation of list
                    embedding = eval(embedding)
                embeddings_list.append(np.array(embedding, dtype=np.float32))
            
            self.embeddings_matrix = np.vstack(embeddings_list)
            logger.info(f"Loaded {len(self.variable_ids)} embeddings")
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise
    
    def _build_index(self):
        """Build FAISS index for efficient similarity search."""
        try:
            logger.info("Building FAISS index")
            
            if not hasattr(self, 'embeddings_matrix') or self.embeddings_matrix is None:
                logger.warning("No embeddings matrix available, skipping index build")
                return
            
            # Normalize embeddings for cosine similarity
            logger.info(f"Normalizing {len(self.embeddings_matrix)} embeddings...")
            faiss.normalize_L2(self.embeddings_matrix)
            
            # Create FAISS index
            logger.info("Creating FAISS index...")
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            self.index.add(self.embeddings_matrix)
            
            logger.info(f"✅ FAISS index built with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            # Don't raise - allow system to work without FAISS
            self.index = None
    
    def _load_enriched_data(self):
        """Load enriched variable data from JSONL file."""
        try:
            logger.info(f"Loading enriched data from {self.enriched_data_path}")
            
            with open(self.enriched_data_path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    self.enriched_data[data.get('varid', data.get('id'))] = data
            
            logger.info(f"Loaded enriched data for {len(self.enriched_data)} variables")
            
        except Exception as e:
            logger.warning(f"Could not load enriched data: {e}")
    
    def get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """
        Get embedding for a query string.
        For now, this returns None as we need OpenAI API for real-time embedding.
        In production, this would call the embedding API.
        """
        # TODO: Implement OpenAI API call for query embedding
        logger.warning("Query embedding not implemented - using fallback")
        return None
    
    def search_similar_variables(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar variables using FAISS.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (variable_id, similarity_score) tuples
        """
        try:
            # Normalize query embedding
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Search
            distances, indices = self.index.search(query_embedding, k)
            
            # Convert to results
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.variable_ids):
                    var_id = self.variable_ids[idx]
                    results.append((var_id, float(dist)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []
    
    def get_variable_info(self, variable_id: str) -> Dict[str, Any]:
        """Get enriched information for a variable."""
        return self.enriched_data.get(variable_id, {})
    
    @lru_cache(maxsize=1000)
    def get_variable_embedding(self, variable_id: str) -> Optional[np.ndarray]:
        """Get embedding for a specific variable."""
        try:
            idx = self.variable_ids.index(variable_id)
            return self.embeddings_matrix[idx]
        except ValueError:
            return None
    
    def find_similar_by_variable(self, variable_id: str, k: int = 10) -> List[Tuple[str, float]]:
        """Find variables similar to a given variable."""
        embedding = self.get_variable_embedding(variable_id)
        if embedding is not None:
            return self.search_similar_variables(embedding, k)
        return []


class EmbeddingsCache:
    """Simple cache for embeddings operations."""
    
    def __init__(self, cache_size: int = 1000):
        self.cache_size = cache_size
        self._cache = {}
        self._access_order = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self._cache:
            # Update access order
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache."""
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.cache_size:
            # Remove least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
        
        self._cache[key] = value
        self._access_order.append(key)