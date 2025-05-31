"""
Enhanced Variable Selector - Consolidated from v5
Loads and searches across all variables with embeddings
"""

import json
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class VariableSelector:
    """Enhanced variable selector with semantic search capabilities"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize with full dataset and embeddings"""
        self.variables = {}
        self.variable_ids = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.embeddings = None
        self.faiss_index = None
        self.openai_client = None
        
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Load full dataset
        self._load_full_dataset()
        
    def _load_full_dataset(self):
        """Load the complete variable dataset with embeddings"""
        import os
        
        # Check if running on GCP
        if os.getenv('GAE_APPLICATION') or os.getenv('GOOGLE_CLOUD_PROJECT'):
            self._load_from_gcs()
            return
            
        base_path = Path(__file__).parent.parent / "data" / "embeddings"
        
        try:
            # Try to load from multiple possible locations
            possible_paths = [
                base_path,
                Path(__file__).parent.parent.parent / "data" / "embeddings",
                Path("/Users/myles/Documents/Activation Manager/data/embeddings")
            ]
            
            loaded = False
            for path in possible_paths:
                if path.exists():
                    # Try loading full dataset files
                    vars_file = path / "variables_full.json"
                    ids_file = path / "variable_ids_full.json"
                    embeddings_file = path / "variable_embeddings_full.npy"
                    
                    if vars_file.exists():
                        logger.info(f"Loading variables from {vars_file}")
                        with open(vars_file, "r") as f:
                            self.variables = json.load(f)
                        loaded = True
                    
                    if ids_file.exists():
                        with open(ids_file, "r") as f:
                            self.variable_ids = json.load(f)
                    elif loaded:
                        # Generate IDs from loaded variables
                        self.variable_ids = list(self.variables.keys())
                    
                    if embeddings_file.exists():
                        logger.info(f"Loading embeddings from {embeddings_file}")
                        self.embeddings = np.load(embeddings_file)
                        self._setup_faiss_index()
                    
                    if loaded:
                        break
            
            if not loaded:
                # Try loading from enriched variables file
                enriched_path = Path("/Users/myles/Documents/NL Variable Parser and Suggestion/enriched_variables.jsonl")
                if enriched_path.exists():
                    self._load_enriched_variables(enriched_path)
                    loaded = True
            
            if loaded:
                # Setup TF-IDF for keyword search
                self._setup_tfidf()
                logger.info(f"✅ Loaded {len(self.variables)} variables")
            else:
                logger.warning("⚠️ No variable data found, initializing with empty dataset")
                
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            # Initialize with empty data
            self.variables = {}
            self.variable_ids = []
            
    def _load_enriched_variables(self, path: Path):
        """Load variables from enriched JSONL file"""
        logger.info(f"Loading enriched variables from {path}")
        self.variables = {}
        self.variable_ids = []
        
        with open(path, 'r') as f:
            for line in f:
                try:
                    var = json.loads(line.strip())
                    var_id = var.get('varid', '')
                    if var_id:
                        self.variables[var_id] = {
                            'code': var_id,
                            'description': var.get('description', ''),
                            'category': var.get('category', ''),
                            'type': var.get('product', 'general'),
                            'keywords': var.get('keywords', []),
                            'context': var.get('context', ''),
                            'product': var.get('product', '')
                        }
                        self.variable_ids.append(var_id)
                except Exception as e:
                    continue
                    
    def _setup_tfidf(self):
        """Setup TF-IDF vectorizer for keyword search"""
        if not self.variables:
            return
            
        # Create text corpus from variable descriptions
        corpus = []
        for var_id in self.variable_ids:
            var = self.variables.get(var_id, {})
            text = f"{var.get('description', '')} {var.get('category', '')} {' '.join(var.get('keywords', []))}"
            corpus.append(text)
        
        # Initialize and fit TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
        logger.info("✅ TF-IDF index created")
        
    def _setup_faiss_index(self):
        """Setup FAISS index for semantic search"""
        if self.embeddings is None or len(self.embeddings) == 0:
            return
            
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(self.embeddings.astype('float32'))
        logger.info(f"✅ FAISS index created with {len(self.embeddings)} vectors")
        
    def search(self, query: str, top_k: int = 10, use_semantic: bool = True, 
               use_keyword: bool = True) -> List[Dict[str, Any]]:
        """
        Search for variables using both semantic and keyword search
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            use_semantic: Whether to use semantic search
            use_keyword: Whether to use keyword search
            
        Returns:
            List of matching variables with scores
        """
        results = []
        
        # Keyword search using TF-IDF
        if use_keyword and self.tfidf_matrix is not None:
            keyword_results = self._keyword_search(query, top_k * 2)
            results.extend(keyword_results)
        
        # Semantic search using embeddings
        if use_semantic and self.faiss_index is not None:
            semantic_results = self._semantic_search(query, top_k * 2)
            results.extend(semantic_results)
        
        # Merge and rank results
        merged_results = self._merge_results(results)
        
        # Return top k
        return merged_results[:top_k]
        
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform keyword-based search using TF-IDF"""
        query_vec = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                var_id = self.variable_ids[idx]
                var = self.variables.get(var_id, {})
                results.append({
                    **var,
                    'score': float(similarities[idx]),
                    'match_type': 'keyword'
                })
                
        return results
        
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings"""
        if not self.openai_client:
            return []
            
        try:
            # Get query embedding
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = np.array(response.data[0].embedding).astype('float32')
            
            # Search in FAISS
            distances, indices = self.faiss_index.search(
                query_embedding.reshape(1, -1), 
                top_k
            )
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.variable_ids):
                    var_id = self.variable_ids[idx]
                    var = self.variables.get(var_id, {})
                    results.append({
                        **var,
                        'score': float(1 / (1 + distances[0][i])),  # Convert distance to similarity
                        'match_type': 'semantic'
                    })
                    
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
            
    def _merge_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate results from different search methods"""
        seen = {}
        merged = []
        
        for result in results:
            var_id = result.get('code', '')
            if var_id not in seen:
                seen[var_id] = result
            else:
                # Combine scores if same variable found by multiple methods
                seen[var_id]['score'] = max(seen[var_id]['score'], result['score'])
                if 'match_type' in seen[var_id] and seen[var_id]['match_type'] != result['match_type']:
                    seen[var_id]['match_type'] = 'combined'
        
        # Sort by score
        merged = list(seen.values())
        merged.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return merged
        
    def get_variable_by_id(self, var_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific variable by its ID"""
        return self.variables.get(var_id)
        
    def get_variables_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all variables in a specific category"""
        results = []
        for var_id, var in self.variables.items():
            if var.get('category', '').lower() == category.lower():
                results.append(var)
        return results
        
    def get_variable_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded variables"""
        if not self.variables:
            return {
                'total_variables': 0,
                'categories': {},
                'has_embeddings': False
            }
            
        categories = {}
        for var in self.variables.values():
            cat = var.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
        return {
            'total_variables': len(self.variables),
            'categories': categories,
            'has_embeddings': self.embeddings is not None,
            'embeddings_shape': self.embeddings.shape if self.embeddings is not None else None
        }
    
    def _load_from_gcs(self):
        """Load embeddings from Google Cloud Storage"""
        try:
            from google.cloud import storage
            import tempfile
            import os
            
            logger.info("Loading embeddings from GCS...")
            
            # Initialize GCS client
            client = storage.Client()
            bucket_name = "activation-manager-data"
            bucket = client.bucket(bucket_name)
            
            # Create temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download files
                files_to_download = [
                    "embeddings/variables_full.json",
                    "embeddings/variable_ids_full.json",
                    "embeddings/variable_embeddings_full.npy",
                    "embeddings/all_variables_enriched.jsonl"
                ]
                
                downloaded_files = []
                for gcs_path in files_to_download:
                    blob = bucket.blob(gcs_path)
                    local_path = os.path.join(temp_dir, os.path.basename(gcs_path))
                    
                    if blob.exists():
                        blob.download_to_filename(local_path)
                        logger.info(f"Downloaded {gcs_path}")
                        downloaded_files.append(local_path)
                
                # Try to load from downloaded files
                if downloaded_files:
                    # Load enriched variables if available
                    enriched_path = os.path.join(temp_dir, "all_variables_enriched.jsonl")
                    if os.path.exists(enriched_path):
                        self._load_enriched_variables(Path(enriched_path))
                        
                    # Load embeddings
                    embeddings_path = os.path.join(temp_dir, "variable_embeddings_full.npy")
                    if os.path.exists(embeddings_path):
                        self.embeddings = np.load(embeddings_path)
                        logger.info(f"Loaded embeddings: {self.embeddings.shape}")
                        
                    # Setup search indices
                    self._setup_tfidf()
                    if self.embeddings is not None:
                        self._setup_faiss_index()
                    
                    logger.info("✅ Successfully loaded from GCS")
                else:
                    raise Exception("No files downloaded from GCS")
                    
        except Exception as e:
            logger.warning(f"Failed to load from GCS: {e}")
            logger.info("Falling back to local files or mock data")
            # Continue with normal loading process