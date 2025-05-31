"""Parquet-based variable loader for fast loading and searching"""

import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from .shared_cache import cache

logger = logging.getLogger(__name__)

class ParquetVariableLoader:
    """Load and search variables from Parquet file"""
    
    def __init__(self):
        self.variables_df = None
        self.variables_dict = []
        self.load_variables()
    
    def load_variables(self):
        """Load variables from Parquet file with shared caching"""
        # Try to load from cache first
        cache_key = "parquet_variables_v2"
        cached_data = cache.get(cache_key, max_age_seconds=1800)  # 30 min cache
        
        if cached_data:
            self.variables_df = cached_data['df']
            self.variables_dict = cached_data['dict']
            logger.info(f"🚀 Loaded {len(self.variables_dict)} variables from cache (fast!)")
            return
        
        # Cache miss - load from file
        logger.info("Cache miss - loading from Parquet file...")
        
        # Try multiple possible paths
        possible_paths = [
            Path(__file__).parent.parent.parent / "data" / "variables_2022_can.parquet",  # Development
            Path("data/variables_2022_can.parquet"),  # App Engine (relative to app root)
            Path("/workspace/data/variables_2022_can.parquet"),  # App Engine alternative
            Path("/app/data/variables_2022_can.parquet"),  # Another App Engine path
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Loading variables from {path}")
                try:
                    self.variables_df = pd.read_parquet(path)
                    
                    # Add search optimization columns if missing
                    if 'description_lower' not in self.variables_df.columns:
                        self.variables_df['description_lower'] = self.variables_df['description'].astype(str).str.lower()
                    if 'code_lower' not in self.variables_df.columns:
                        self.variables_df['code_lower'] = self.variables_df['code'].astype(str).str.lower()
                    
                    # Convert to list of dicts for compatibility
                    self.variables_dict = self.variables_df.to_dict('records')
                    
                    # Cache the processed data for other workers
                    cache_data = {
                        'df': self.variables_df,
                        'dict': self.variables_dict
                    }
                    cache.put(cache_key, cache_data)
                    
                    logger.info(f"✅ Loaded {len(self.variables_dict)} variables from Parquet and cached")
                    return
                except Exception as e:
                    logger.error(f"Failed to load Parquet file from {path}: {e}")
        
        logger.error("Parquet file not found in any of the expected locations")
        self.variables_df = pd.DataFrame()
        self.variables_dict = []
    
    def get_all_variables(self) -> List[Dict[str, Any]]:
        """Get all variables as list of dictionaries"""
        return self.variables_dict
    
    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fast search using pandas operations"""
        if self.variables_df is None or self.variables_df.empty:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Create a copy to work with
        df = self.variables_df.copy()
        
        # Score based on matches
        df['score'] = 0
        
        # Exact description match
        df.loc[df['description_lower'].str.contains(query_lower, na=False), 'score'] += 50
        
        # Exact code match
        df.loc[df['code_lower'].str.contains(query_lower, na=False), 'score'] += 30
        
        # Word matches in description
        for word in query_words:
            df.loc[df['description_lower'].str.contains(word, na=False), 'score'] += 10
        
        # Filter and sort
        results = df[df['score'] > 0].nlargest(limit, 'score')
        
        # Convert to list of dicts
        return results.to_dict('records')