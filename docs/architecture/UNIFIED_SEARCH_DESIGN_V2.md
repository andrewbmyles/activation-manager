# Unified Search Architecture Design V2
## With Performance & Enhancement Preservation

## Critical Requirements

To ensure we maintain the performance gains and enhancements achieved:

### 1. **Similarity Filtering Performance** 
- **Current**: Reduces "Contact with friends" patterns from 50 to 1 (98% reduction)
- **Must Preserve**: 
  - Jaro-Winkler algorithm with base pattern grouping
  - Aggressive filtering within groups (threshold: 0.75)
  - Max 2 representatives per group
  - Special handling for empty descriptions

### 2. **Search Performance**
- **Current**: <100ms latency for 50k variables
- **Must Preserve**:
  - Pandas vectorized operations for keyword search
  - FAISS flat index for semantic search
  - Lazy loading with singleton pattern
  - Parquet data format (5-10x faster than CSV)

### 3. **Enhanced Features**
- **Current**: Advanced query understanding, concept extraction
- **Must Preserve**:
  - Multi-concept query handling
  - Domain-specific optimizations
  - Numeric pattern recognition
  - Fallback search when enhanced search unavailable

## Revised Architecture

### Core Principle: "Enhance, Don't Replace"

Instead of a complete rewrite, we'll refactor by:
1. Extracting common code into shared modules
2. Keeping proven algorithms intact
3. Creating a unified interface over existing implementations
4. Gradual migration with feature flags

### Phased Approach

```
Phase 1: Extract & Modularize (Week 2)
├── Extract similarity_filter.py logic (DONE ✓)
├── Create shared configuration module
├── Extract domain configs
└── Create unified data model

Phase 2: Create Unified Interface (Week 2-3)
├── Wrapper over existing implementations
├── Feature flag system
├── Performance monitoring
└── A/B testing framework

Phase 3: Gradual Internal Refactoring (Week 3-4)
├── Consolidate duplicate code
├── Optimize memory usage
├── Improve test coverage
└── Documentation
```

## Detailed Design with Performance Preservation

### 1. Configuration Module (New)

```python
# activation_manager/search/config.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SearchConfig:
    """Centralized configuration for search"""
    # Performance settings
    use_lazy_loading: bool = True
    cache_ttl: int = 900  # 15 minutes
    max_results_before_filter: int = 100  # Get extra for filtering
    
    # Filtering settings (preserve current values)
    filter_similar: bool = True
    similarity_threshold: float = 0.75  # Proven threshold
    max_similar_per_group: int = 2     # Proven limit
    
    # Search weights (preserve current hybrid weights)
    keyword_weight: float = 0.3
    semantic_weight: float = 0.7
    
    # Domain configs (extract from current)
    domain_configs: Dict[str, Any] = None
    
    # Feature flags
    use_enhanced_search_v2: bool = True
    use_concept_extraction: bool = True
    fallback_on_error: bool = True
    
    @classmethod
    def load_from_env(cls) -> 'SearchConfig':
        """Load config from environment with current defaults"""
        # Preserves all current settings
```

### 2. Unified Search Interface (Wrapper Pattern)

```python
# activation_manager/search/unified_search.py
from typing import Dict, Any, Optional
import logging
from ..core.enhanced_semantic_search_v2 import EnhancedSemanticSearchV2
from ..core.similarity_filter import filter_similar_variables
from .config import SearchConfig

logger = logging.getLogger(__name__)

class UnifiedSearch:
    """
    Unified interface that wraps existing implementations
    Preserves all current functionality and performance
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        self.config = config or SearchConfig.load_from_env()
        self._search_engine = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Lazy initialization (preserves current pattern)"""
        if self._initialized:
            return True
            
        try:
            if self.config.use_enhanced_search_v2:
                # Use existing enhanced search v2
                from ..core.enhanced_parquet_loader import EnhancedParquetLoader
                loader = EnhancedParquetLoader()
                variables = loader.get_all_variables()
                
                self._search_engine = EnhancedSemanticSearchV2(
                    variables=variables,
                    embeddings=None,  # Lazy load
                    openai_api_key=self.config.openai_api_key
                )
            else:
                # Fallback to v1 or basic search
                pass
                
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Search initialization failed: {e}")
            if self.config.fallback_on_error:
                self._initialize_fallback()
            return False
    
    def search(self, query: str, top_k: int = 50, **kwargs) -> Dict[str, Any]:
        """
        Unified search that preserves all current functionality
        
        Performance guarantee: <100ms for 50k variables
        Filtering guarantee: 98% reduction in duplicates
        """
        self._ensure_initialized()
        
        # Override with config defaults
        filter_similar = kwargs.get('filter_similar', self.config.filter_similar)
        similarity_threshold = kwargs.get('similarity_threshold', self.config.similarity_threshold)
        max_similar_per_group = kwargs.get('max_similar_per_group', self.config.max_similar_per_group)
        
        # Use existing search engine
        if self._search_engine:
            # Get extra results for filtering
            search_top_k = top_k * 2 if filter_similar else top_k
            
            results = self._search_engine.search(
                query=query,
                top_k=search_top_k,
                filter_similar=False,  # We'll filter separately for consistency
                **kwargs
            )
            
            # Apply filtering using proven algorithm
            if filter_similar and results.get('results'):
                original_count = len(results['results'])
                filtered = filter_similar_variables(
                    results['results'],
                    similarity_threshold=similarity_threshold,
                    max_similar_per_group=max_similar_per_group
                )
                results['results'] = filtered[:top_k]
                results['total_found'] = len(filtered)
                
                logger.info(f"Filtering: {original_count} → {len(filtered)} results")
                
        else:
            # Fallback implementation
            results = self._fallback_search(query, top_k, **kwargs)
            
        return results
```

### 3. Shared Modules (Extract Common Code)

```python
# activation_manager/search/shared/domain_configs.py
"""Extract domain configurations to single source"""

DOMAIN_CONFIGS = {
    "automotive": {
        "name": "Automotive",
        "priority_terms": ["car", "vehicle", "auto", "drive"],
        "boosts": {
            "exact_match": 2.0,
            "prefix_match": 1.5,
            "semantic": 1.3
        }
    },
    # ... rest of domains
}

# activation_manager/search/shared/numeric_patterns.py
"""Extract numeric pattern matching"""

import re
from typing import List, Tuple

def extract_numeric_patterns(text: str) -> List[Tuple[float, float]]:
    """Extract numeric patterns from text (proven algorithm)"""
    # Exact implementation from current code
    patterns = []
    
    # Age ranges
    age_pattern = r'(?:age[s]?\s+)?(\d+)\s*[-to]+\s*(\d+)'
    # ... rest of patterns
    
    return patterns
```

### 4. Performance Monitoring

```python
# activation_manager/search/monitoring.py
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def monitor_performance(operation: str):
    """Decorator to monitor search performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000  # ms
                
                if elapsed > 100:  # Alert if >100ms
                    logger.warning(f"{operation} took {elapsed:.2f}ms")
                else:
                    logger.debug(f"{operation} took {elapsed:.2f}ms")
                    
                return result
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                logger.error(f"{operation} failed after {elapsed:.2f}ms: {e}")
                raise
        return wrapper
    return decorator

class PerformanceBaseline:
    """Track performance against baseline"""
    BASELINES = {
        'search_latency': 100,  # ms
        'filter_reduction': 0.98,  # 98% reduction
        'memory_usage': 512,  # MB
    }
    
    @classmethod
    def check_performance(cls, metric: str, value: float) -> bool:
        """Check if performance meets baseline"""
        baseline = cls.BASELINES.get(metric)
        if not baseline:
            return True
            
        if metric == 'search_latency':
            return value <= baseline
        elif metric == 'filter_reduction':
            return value >= baseline
        elif metric == 'memory_usage':
            return value <= baseline
            
        return True
```

### 5. Migration Strategy with Feature Flags

```python
# activation_manager/search/migration.py
from typing import Dict, Any
import random

class SearchMigration:
    """Handle gradual migration with A/B testing"""
    
    def __init__(self, rollout_percentage: float = 0.0):
        self.rollout_percentage = rollout_percentage
        self.legacy_search = None  # Current implementation
        self.unified_search = None  # New implementation
        
    def should_use_unified(self, user_id: str = None) -> bool:
        """Determine which search to use"""
        if self.rollout_percentage >= 100:
            return True
        if self.rollout_percentage <= 0:
            return False
            
        # Consistent hashing for user
        if user_id:
            hash_value = hash(user_id) % 100
            return hash_value < self.rollout_percentage
        else:
            return random.random() < (self.rollout_percentage / 100)
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Route to appropriate search"""
        use_unified = self.should_use_unified(kwargs.get('user_id'))
        
        if use_unified and self.unified_search:
            result = self.unified_search.search(query, **kwargs)
            result['_search_version'] = 'unified'
        else:
            result = self.legacy_search.search(query, **kwargs)
            result['_search_version'] = 'legacy'
            
        # Log for comparison
        self._log_search_metrics(query, result)
        
        return result
```

## Testing Strategy

### 1. Performance Tests

```python
# tests/performance/test_search_performance.py
import pytest
import time
from activation_manager.search import UnifiedSearch

class TestSearchPerformance:
    
    @pytest.mark.performance
    def test_search_latency(self, search_engine):
        """Ensure <100ms search latency"""
        queries = [
            "contact with friends income",
            "millennials high income automotive",
            "household income over 100k"
        ]
        
        for query in queries:
            start = time.time()
            results = search_engine.search(query, top_k=50)
            elapsed = (time.time() - start) * 1000
            
            assert elapsed < 100, f"Search took {elapsed}ms, expected <100ms"
            assert results['total_found'] > 0
    
    @pytest.mark.performance  
    def test_filter_reduction(self, search_engine):
        """Ensure 98% reduction in duplicates"""
        # Test with known duplicate-heavy query
        results_no_filter = search_engine.search(
            "contact with friends", 
            filter_similar=False
        )
        
        results_filtered = search_engine.search(
            "contact with friends",
            filter_similar=True,
            similarity_threshold=0.75,
            max_similar_per_group=2
        )
        
        reduction = 1 - (results_filtered['total_found'] / results_no_filter['total_found'])
        assert reduction >= 0.95, f"Only {reduction*100}% reduction, expected >=95%"
```

### 2. Compatibility Tests

```python
# tests/compatibility/test_api_compatibility.py
import pytest
from activation_manager.search import UnifiedSearch
from activation_manager.core.enhanced_semantic_search_v2 import EnhancedSemanticSearchV2

class TestAPICompatibility:
    
    def test_search_interface_compatible(self):
        """Ensure unified search maintains same interface"""
        unified = UnifiedSearch()
        legacy = EnhancedSemanticSearchV2([], None, None)
        
        # Check method signatures match
        unified_sig = inspect.signature(unified.search)
        legacy_sig = inspect.signature(legacy.search)
        
        # Verify parameters
        assert set(unified_sig.parameters.keys()) >= set(legacy_sig.parameters.keys())
    
    def test_response_format_compatible(self):
        """Ensure response format unchanged"""
        unified = UnifiedSearch()
        result = unified.search("test query")
        
        # Check required fields
        assert 'results' in result
        assert 'total_found' in result
        assert 'query_context' in result
        assert isinstance(result['results'], list)
```

## Implementation Timeline

### Week 2: Foundation
- [x] Day 1: Create similarity_filter.py (DONE)
- [ ] Day 2: Extract domain configs and shared utilities
- [ ] Day 3: Create unified search wrapper
- [ ] Day 4: Add performance monitoring
- [ ] Day 5: Create comprehensive tests

### Week 3: Integration
- [ ] Day 1-2: Integrate unified search with API
- [ ] Day 3: Add feature flags and migration logic
- [ ] Day 4: Performance testing and optimization
- [ ] Day 5: A/B testing setup

### Week 4: Rollout
- [ ] Day 1: Deploy with 0% rollout
- [ ] Day 2: 10% rollout, monitor metrics
- [ ] Day 3: 50% rollout if metrics good
- [ ] Day 4: 100% rollout
- [ ] Day 5: Remove legacy code (optional)

## Risk Mitigation

1. **Performance Regression**
   - Continuous monitoring against baselines
   - Automatic rollback if performance degrades
   - A/B testing to compare implementations

2. **Feature Loss**
   - Comprehensive test coverage
   - Feature flag for each major component
   - Gradual rollout with monitoring

3. **Breaking Changes**
   - Wrapper pattern preserves exact API
   - All changes internal only
   - Extensive compatibility testing

## Success Criteria

1. **Performance**: All searches <100ms (current baseline)
2. **Filtering**: ≥95% reduction in duplicates (current: 98%)
3. **Accuracy**: A/B tests show equivalent or better results
4. **Reliability**: No increase in error rate
5. **Maintainability**: 50% reduction in code duplication

This revised design ensures we preserve all the performance gains and enhancements while still achieving the refactoring goals.