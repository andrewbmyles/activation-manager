"""
Enhanced Parquet Variable Loader
Optimized for performance with the full 49,323 variable dataset
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

logger = logging.getLogger(__name__)


class EnhancedParquetLoader:
    """
    Enhanced Parquet loader with better performance and search capabilities
    Advantages over CSV:
    - 5-10x faster loading
    - Built-in compression
    - Preserves data types
    - Efficient columnar storage
    """
    
    def __init__(self, parquet_path: Optional[str] = None):
        """Initialize the enhanced parquet loader"""
        self.variables_df = None
        self.variables_dict = {}
        self.variable_list = []
        
        # Find parquet file
        if parquet_path:
            self.parquet_path = Path(parquet_path)
        else:
            self.parquet_path = self._find_parquet_file()
        
        # Load data
        self.load_variables()
    
    def _find_parquet_file(self) -> Optional[Path]:
        """Find the parquet file in common locations"""
        possible_paths = [
            Path(__file__).parent.parent.parent / "data" / "variables_2022_can.parquet",
            Path("/Users/myles/Documents/Activation Manager/data/variables_2022_can.parquet"),
            Path("/srv/data/variables_2022_can.parquet"),  # App Engine
            Path("data/variables_2022_can.parquet"),  # Relative
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        logger.error("Parquet file not found in any expected location")
        return None
    
    def load_variables(self) -> bool:
        """Load variables from parquet file"""
        if not self.parquet_path or not self.parquet_path.exists():
            logger.error(f"Parquet file not found: {self.parquet_path}")
            return False
        
        try:
            start_time = time.time()
            
            # Load parquet file
            self.variables_df = pd.read_parquet(self.parquet_path)
            
            # Ensure required columns exist
            required_cols = ['code', 'description', 'theme', 'ProductName', 'category']
            missing_cols = [col for col in required_cols if col not in self.variables_df.columns]
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}")
            
            # Add lowercase columns if not present
            if 'code_lower' not in self.variables_df.columns:
                self.variables_df['code_lower'] = self.variables_df['code'].str.lower()
            if 'description_lower' not in self.variables_df.columns:
                self.variables_df['description_lower'] = self.variables_df['description'].str.lower()
            
            # Create dictionaries for fast lookup
            self._build_lookup_structures()
            
            load_time = time.time() - start_time
            logger.info(f"✅ Loaded {len(self.variables_df)} variables from parquet in {load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load parquet file: {e}")
            return False
    
    def _build_lookup_structures(self):
        """Build efficient lookup structures"""
        # Convert to list of dicts for compatibility
        self.variable_list = self.variables_df.to_dict('records')
        
        # Build code -> variable dict for O(1) lookup
        self.variables_dict = {
            row['code']: row for row in self.variable_list
        }
        
        # Build category index
        self.category_index = {}
        for var in self.variable_list:
            cat = var.get('category', 'Unknown')
            if cat not in self.category_index:
                self.category_index[cat] = []
            self.category_index[cat].append(var)
        
        # Build theme index
        self.theme_index = {}
        for var in self.variable_list:
            theme = var.get('theme', 'Unknown')
            if theme not in self.theme_index:
                self.theme_index[theme] = []
            self.theme_index[theme].append(var)
    
    def get_all_variables(self) -> List[Dict[str, Any]]:
        """Get all variables as list of dictionaries"""
        return self.variable_list
    
    def get_variable_by_id(self, var_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific variable by ID - O(1) lookup"""
        return self.variables_dict.get(var_id.upper())
    
    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fast search using pandas vectorized operations
        Much faster than iterating through 49k records
        """
        if self.variables_df is None or self.variables_df.empty:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Create scoring dataframe
        df = self.variables_df.copy()
        df['score'] = 0.0
        
        # Exact code match (highest priority)
        df.loc[df['code_lower'] == query_lower, 'score'] += 100
        
        # Code contains query
        df.loc[df['code_lower'].str.contains(query_lower, na=False), 'score'] += 50
        
        # Exact description match
        df.loc[df['description_lower'] == query_lower, 'score'] += 80
        
        # Description contains full query
        df.loc[df['description_lower'].str.contains(query_lower, na=False), 'score'] += 40
        
        # Word-by-word matching
        for word in query_words:
            if len(word) > 2:  # Skip short words
                # Word in description
                df.loc[df['description_lower'].str.contains(f'\\b{word}\\b', regex=True, na=False), 'score'] += 10
                # Word in code
                df.loc[df['code_lower'].str.contains(word, na=False), 'score'] += 15
                # Word in category
                if 'category' in df.columns:
                    df.loc[df['category'].str.lower().str.contains(word, na=False), 'score'] += 8
                # Word in theme
                if 'theme' in df.columns:
                    df.loc[df['theme'].str.lower().str.contains(word, na=False), 'score'] += 5
        
        # Filter and sort
        results = df[df['score'] > 0].nlargest(limit, 'score')
        
        # Convert to list of dicts with scores
        results_list = []
        for _, row in results.iterrows():
            var_dict = row.to_dict()
            var_dict['search_score'] = var_dict.pop('score')
            # Remove helper columns
            var_dict.pop('code_lower', None)
            var_dict.pop('description_lower', None)
            results_list.append(var_dict)
        
        return results_list
    
    def get_variables_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all variables in a category - uses pre-built index"""
        return self.category_index.get(category, [])
    
    def get_variables_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """Get all variables in a theme - uses pre-built index"""
        return self.theme_index.get(theme, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        if self.variables_df is None or self.variables_df.empty:
            return {'error': 'No data loaded'}
        
        return {
            'total_variables': len(self.variables_df),
            'themes': self.variables_df['theme'].value_counts().to_dict(),
            'products': self.variables_df['ProductName'].value_counts().to_dict(),
            'categories': len(self.variables_df['category'].unique()),
            'data_source': str(self.parquet_path),
            'columns': list(self.variables_df.columns)
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Get the raw dataframe for advanced operations"""
        return self.variables_df.copy()


# Convenience function for backward compatibility
def load_variables_from_parquet(parquet_path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Load variables from parquet file
    Returns: (list of variable dicts, pandas DataFrame)
    """
    loader = EnhancedParquetLoader(parquet_path)
    return loader.get_all_variables(), loader.to_dataframe()