"""
Centralized configuration for unified search
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
from .shared.domain_configs import DOMAIN_CONFIGS


@dataclass
class SearchConfig:
    """Centralized configuration for search with proven defaults"""
    
    # Performance settings (preserve current values)
    use_lazy_loading: bool = True
    cache_ttl: int = 900  # 15 minutes
    max_results_before_filter: int = 100  # Get extra results for filtering
    default_top_k: int = 50  # Changed from 10 to 50 in v1.3.0
    
    # Filtering settings (proven values from production)
    filter_similar: bool = True
    similarity_threshold: float = 0.75  # Proven threshold - reduces Contact patterns by 98%
    max_similar_per_group: int = 2     # Proven limit - max 2 per pattern
    
    # Search weights (preserve current hybrid weights)
    keyword_weight: float = 0.3
    semantic_weight: float = 0.7
    
    # BM25 parameters (from current implementation)
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    
    # Scoring boosts (from current implementation)
    exact_match_boost: float = 2.0
    prefix_match_boost: float = 1.5
    negative_keyword_penalty: float = 0.5
    
    # Domain configurations
    domain_configs: Dict[str, Any] = field(default_factory=lambda: DOMAIN_CONFIGS)
    
    # Feature flags
    use_enhanced_search_v2: bool = True
    use_concept_extraction: bool = True
    use_advanced_processing: bool = True
    fallback_on_error: bool = True
    
    # Embeddings configuration
    use_embeddings: bool = field(default_factory=lambda: os.environ.get('USE_EMBEDDINGS', 'true').lower() == 'true')
    embedding_load_strategy: str = field(default_factory=lambda: os.environ.get('EMBEDDING_LOAD_STRATEGY', 'lazy'))
    
    # API keys
    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get('OPENAI_API_KEY'))
    
    # Data sources
    parquet_path: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'data', 
        'Full_Variable_List_2024_CAN.parquet'
    ))
    csv_path: str = field(default_factory=lambda: os.environ.get(
        'CSV_PATH',
        '/Users/myles/Documents/Data Dictionary for APIs from DaaS/Full_Variable_List_2022_CAN.csv'
    ))
    
    # Performance monitoring
    monitor_performance: bool = True
    performance_log_threshold: float = 100.0  # Log if search takes >100ms
    
    # A/B testing
    enable_ab_testing: bool = False
    unified_rollout_percentage: float = 0.0  # Start with 0% rollout
    
    @classmethod
    def load_from_env(cls) -> 'SearchConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        if os.environ.get('FILTER_SIMILAR'):
            config.filter_similar = os.environ.get('FILTER_SIMILAR', 'true').lower() == 'true'
        
        if os.environ.get('SIMILARITY_THRESHOLD'):
            config.similarity_threshold = float(os.environ.get('SIMILARITY_THRESHOLD', '0.75'))
            
        if os.environ.get('MAX_SIMILAR_PER_GROUP'):
            config.max_similar_per_group = int(os.environ.get('MAX_SIMILAR_PER_GROUP', '2'))
            
        if os.environ.get('DEFAULT_TOP_K'):
            config.default_top_k = int(os.environ.get('DEFAULT_TOP_K', '50'))
            
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging"""
        return {
            'filter_similar': self.filter_similar,
            'similarity_threshold': self.similarity_threshold,
            'max_similar_per_group': self.max_similar_per_group,
            'default_top_k': self.default_top_k,
            'keyword_weight': self.keyword_weight,
            'semantic_weight': self.semantic_weight,
            'use_enhanced_search_v2': self.use_enhanced_search_v2,
            'use_embeddings': self.use_embeddings,
            'unified_rollout_percentage': self.unified_rollout_percentage
        }