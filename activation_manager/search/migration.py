"""
Migration utilities for gradual rollout of unified search
"""
import logging
import hashlib
from typing import Dict, Any, Optional
from .config import SearchConfig
from .unified_search import UnifiedSearch
from ..api.enhanced_variable_picker_api import EnhancedVariablePickerAPI

logger = logging.getLogger(__name__)


class SearchMigration:
    """
    Handle gradual migration from legacy to unified search
    Enables A/B testing and safe rollout
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        self.config = config or SearchConfig.load_from_env()
        self.unified_search = None
        self.legacy_search = None
        self._metrics = {
            'unified_calls': 0,
            'legacy_calls': 0,
            'unified_errors': 0,
            'legacy_errors': 0
        }
        
    def _ensure_initialized(self):
        """Initialize both search implementations"""
        if not self.unified_search:
            self.unified_search = UnifiedSearch.get_instance(self.config)
            
        if not self.legacy_search:
            self.legacy_search = EnhancedVariablePickerAPI.get_instance(
                self.config.openai_api_key
            )
    
    def should_use_unified(self, user_id: Optional[str] = None, 
                          query: Optional[str] = None) -> bool:
        """
        Determine whether to use unified search
        
        Args:
            user_id: Optional user identifier for consistent routing
            query: Optional query for query-based routing
            
        Returns:
            True if should use unified search, False for legacy
        """
        if not self.config.enable_ab_testing:
            return False
            
        rollout_percentage = self.config.unified_rollout_percentage
        
        # 100% rollout
        if rollout_percentage >= 100:
            return True
            
        # 0% rollout
        if rollout_percentage <= 0:
            return False
        
        # Consistent hashing for user-based routing
        if user_id:
            hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            user_bucket = hash_value % 100
            return user_bucket < rollout_percentage
        
        # Query-based routing (for testing specific queries)
        if query and self._is_test_query(query):
            return True
            
        # Random sampling fallback
        import random
        return random.random() * 100 < rollout_percentage
    
    def _is_test_query(self, query: str) -> bool:
        """Check if query is a test query that should use unified search"""
        test_patterns = [
            'unified_test',
            'test_unified_search',
            '_unified_'
        ]
        return any(pattern in query.lower() for pattern in test_patterns)
    
    def search(self, query: str, top_k: int = 50, 
               user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Route search to appropriate implementation
        
        Args:
            query: Search query
            top_k: Number of results
            user_id: Optional user ID for consistent routing
            **kwargs: Additional search parameters
            
        Returns:
            Search results with metadata about which implementation was used
        """
        self._ensure_initialized()
        
        use_unified = self.should_use_unified(user_id, query)
        
        try:
            if use_unified:
                logger.debug(f"Routing to unified search: {query[:50]}...")
                self._metrics['unified_calls'] += 1
                
                result = self.unified_search.search(query, top_k, **kwargs)
                result['_implementation'] = 'unified'
                
            else:
                logger.debug(f"Routing to legacy search: {query[:50]}...")
                self._metrics['legacy_calls'] += 1
                
                result = self.legacy_search.search_variables(query, top_k, **kwargs)
                result['_implementation'] = 'legacy'
            
            # Log for comparison if in A/B test mode
            if 0 < self.config.unified_rollout_percentage < 100:
                self._log_ab_test_result(query, result, use_unified)
                
            return result
            
        except Exception as e:
            logger.error(f"Search failed with {'unified' if use_unified else 'legacy'}: {e}")
            
            if use_unified:
                self._metrics['unified_errors'] += 1
            else:
                self._metrics['legacy_errors'] += 1
                
            # Try fallback to other implementation
            if self.config.fallback_on_error:
                try:
                    if use_unified:
                        # Fallback to legacy
                        logger.info("Falling back to legacy search")
                        result = self.legacy_search.search_variables(query, top_k, **kwargs)
                        result['_implementation'] = 'legacy'
                        result['_fallback'] = True
                    else:
                        # Fallback to unified
                        logger.info("Falling back to unified search")
                        result = self.unified_search.search(query, top_k, **kwargs)
                        result['_implementation'] = 'unified'
                        result['_fallback'] = True
                        
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    
            # Return error response
            return {
                'results': [],
                'total_found': 0,
                'error': str(e),
                '_implementation': 'unified' if use_unified else 'legacy',
                '_error': True
            }
    
    def _log_ab_test_result(self, query: str, result: Dict[str, Any], used_unified: bool):
        """Log results for A/B test comparison"""
        log_entry = {
            'query': query[:100],  # First 100 chars
            'implementation': 'unified' if used_unified else 'legacy',
            'total_found': result.get('total_found', 0),
            'result_count': len(result.get('results', [])),
            'has_error': 'error' in result,
            'response_time': result.get('_response_time_ms')  # If added by monitoring
        }
        
        # Log to a format that can be analyzed later
        logger.info(f"AB_TEST_RESULT: {log_entry}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get migration metrics"""
        total_calls = self._metrics['unified_calls'] + self._metrics['legacy_calls']
        
        return {
            'total_calls': total_calls,
            'unified_percentage': (self._metrics['unified_calls'] / total_calls * 100) if total_calls > 0 else 0,
            'unified_calls': self._metrics['unified_calls'],
            'legacy_calls': self._metrics['legacy_calls'],
            'unified_error_rate': (self._metrics['unified_errors'] / self._metrics['unified_calls']) if self._metrics['unified_calls'] > 0 else 0,
            'legacy_error_rate': (self._metrics['legacy_errors'] / self._metrics['legacy_calls']) if self._metrics['legacy_calls'] > 0 else 0,
            'rollout_percentage': self.config.unified_rollout_percentage
        }


# Global migration instance
_migration = None


def get_migration_instance(config: Optional[SearchConfig] = None) -> SearchMigration:
    """Get global migration instance"""
    global _migration
    if _migration is None:
        _migration = SearchMigration(config)
    return _migration


def search_with_migration(query: str, top_k: int = 50, 
                         user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Convenience function for migrated search"""
    migration = get_migration_instance()
    return migration.search(query, top_k, user_id, **kwargs)