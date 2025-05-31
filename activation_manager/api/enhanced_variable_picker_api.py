"""
Enhanced Variable Picker API
Integrates the enhanced semantic search with 50-result capability
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from ..core.shared_cache import cache

logger = logging.getLogger(__name__)

# Global singleton instance
_enhanced_picker_instance = None
_initialization_attempted = False

class EnhancedVariablePickerAPI:
    """Enhanced API for variable selection with 50-result semantic search"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize enhanced variable picker with lazy loading"""
        self.openai_api_key = openai_api_key
        self.enhanced_search = None
        self.variable_selector = None
        self.query_optimizer = None
        self._initialized = False
        
        # Don't initialize heavy components in __init__
        logger.info("✅ Enhanced Variable Picker API created (lazy initialization)")
    
    @classmethod
    def get_instance(cls, openai_api_key: Optional[str] = None):
        """Get singleton instance"""
        global _enhanced_picker_instance, _initialization_attempted
        
        if _enhanced_picker_instance is None and not _initialization_attempted:
            _initialization_attempted = True
            try:
                _enhanced_picker_instance = cls(openai_api_key)
                logger.info("✅ Enhanced Variable Picker singleton created")
            except Exception as e:
                logger.warning(f"Failed to create Enhanced Variable Picker: {e}")
                _enhanced_picker_instance = None
        
        return _enhanced_picker_instance
    
    def _ensure_initialized(self):
        """Lazy initialization of heavy components with caching and retry logic"""
        if self._initialized:
            return True
        
        # Add retry logic for robustness
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Initializing Enhanced Variable Picker (attempt {attempt + 1}/{max_retries})...")
                
                # Check if we can skip FAISS loading by using cache
                cache_key = "enhanced_picker_ready_v2"
                cached_status = cache.get(cache_key)
                if cached_status:
                    logger.info("🚀 Enhanced picker components already cached by another worker")
                    # Still need to load basic components, but can skip heavy FAISS
                    from ..core.semantic_query_optimizer import SemanticQueryOptimizer
                    self.query_optimizer = SemanticQueryOptimizer()
                    self._initialized = True
                    return True
                
                # Import only when needed to avoid startup overhead
                from ..core.variable_selector import VariableSelector
                from ..core.enhanced_semantic_search_v2 import EnhancedSemanticSearchV2
                from ..core.enhanced_parquet_loader import EnhancedParquetLoader
                from ..core.semantic_query_optimizer import SemanticQueryOptimizer
                
                # Initialize query optimizer (lightweight)
                self.query_optimizer = SemanticQueryOptimizer()
                
                # Store parquet loader for fallback
                self.parquet_loader = EnhancedParquetLoader()
                
                if self.parquet_loader.variables_df is not None and not self.parquet_loader.variables_df.empty:
                    variables_list = self.parquet_loader.get_all_variables()
                    
                    # Skip embeddings if disabled
                    use_embeddings = os.environ.get('USE_EMBEDDINGS', 'true').lower() == 'true'
                    embeddings = None
                    
                    if use_embeddings:
                        try:
                            logger.info("Loading FAISS embeddings...")
                            self.variable_selector = VariableSelector(openai_api_key=self.openai_api_key)
                            if hasattr(self.variable_selector, 'embeddings'):
                                embeddings = self.variable_selector.embeddings
                                logger.info("✅ FAISS embeddings loaded")
                        except Exception as e:
                            logger.warning(f"Could not load embeddings: {e}")
                    else:
                        logger.info("📌 Embeddings disabled by configuration")
                    
                    # Initialize enhanced search V2 with parquet data
                    logger.info("Creating EnhancedSemanticSearchV2...")
                    self.enhanced_search = EnhancedSemanticSearchV2(
                        variables=variables_list,
                        embeddings=embeddings,
                        openai_api_key=self.openai_api_key
                    )
                    logger.info("✅ EnhancedSemanticSearchV2 created successfully")
                    
                    # Mark as ready in cache so other workers know
                    cache.put(cache_key, True)
                    
                    logger.info(f"✅ Enhanced search initialized with {len(variables_list)} variables from Parquet")
                    self._initialized = True
                    return True
                else:
                    logger.warning("No variables loaded from Parquet")
                    
            except Exception as e:
                logger.error(f"Initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
        
        # All retries failed - mark as initialized anyway to prevent infinite retries
        logger.error("Enhanced search initialization failed after all retries")
        self._initialized = True
        return False
    
    def _load_from_csv(self):
        """Load variables from CSV as fallback"""
        try:
            # Try multiple possible paths for the CSV
            possible_paths = [
                Path("/Users/myles/Documents/Data Dictionary for APIs from DaaS/Full_Variable_List_2022_CAN.csv"),
                Path("../Data Dictionary for APIs from DaaS/Full_Variable_List_2022_CAN.csv"),
                Path("data/Full_Variable_List_2022_CAN.csv")
            ]
            
            csv_path = None
            for path in possible_paths:
                if path.exists():
                    csv_path = path
                    break
            
            if csv_path:
                loader = CSVVariableLoader(str(csv_path))
                variables_df = loader.load_variables()
                
                # Convert to list of dicts
                variables_list = variables_df.to_dict('records')
                
                # Initialize enhanced search V2 without embeddings
                self.enhanced_search = EnhancedSemanticSearchV2(
                    variables=variables_list,
                    embeddings=None,
                    openai_api_key=self.openai_api_key
                )
                
                logger.info(f"✅ Loaded {len(variables_list)} variables from CSV")
            else:
                logger.error("Could not find variable CSV file")
                
        except Exception as e:
            logger.error(f"Error loading from CSV: {e}")
    
    def _basic_parquet_search(self, query: str, top_k: int = 50, 
                             filter_similar: bool = False,
                             similarity_threshold: float = 0.85,
                             max_similar_per_group: int = 2) -> Dict[str, Any]:
        """Basic fallback search using parquet loader directly"""
        try:
            if not hasattr(self, 'parquet_loader') or self.parquet_loader is None:
                from ..core.enhanced_parquet_loader import EnhancedParquetLoader
                self.parquet_loader = EnhancedParquetLoader()
            
            if self.parquet_loader and hasattr(self.parquet_loader, 'search'):
                # Use parquet loader's search method
                results = self.parquet_loader.search(query, top_k)
                
                # Apply similarity filtering if requested
                if filter_similar and results:
                    logger.info(f"📍 Applying filtering in fallback search: {len(results)} results")
                    # Import the standalone filtering function
                    try:
                        from ..core.similarity_filter import filter_similar_variables
                        filtered_results = filter_similar_variables(
                            results,
                            similarity_threshold=similarity_threshold,
                            max_similar_per_group=max_similar_per_group
                        )
                        logger.info(f"✅ Fallback filtering: {len(results)} → {len(filtered_results)} results")
                        results = filtered_results
                    except Exception as e:
                        logger.error(f"Filtering failed in fallback: {e}")
                
                return {
                    'results': results,
                    'total_found': len(results),
                    'query_context': {'original_query': query},
                    'search_methods': {'keyword': True, 'semantic': False},
                    'fallback_mode': True,
                    'filter_similar': filter_similar,
                    'message': 'Using basic search (enhanced search unavailable)'
                }
            else:
                return {
                    'results': [],
                    'total_found': 0,
                    'error': 'No search backend available',
                    'query_context': {'original_query': query}
                }
        except Exception as e:
            logger.error(f"Basic parquet search failed: {e}")
            return {
                'results': [],
                'total_found': 0,
                'error': f'Search failed: {str(e)}',
                'query_context': {'original_query': query}
            }
    
    def search_variables(self, query: str, top_k: int = 50, 
                        use_semantic: bool = True, 
                        use_keyword: bool = True,
                        filters: Optional[Dict] = None,
                        use_advanced_processing: bool = True,
                        filter_similar: bool = False,
                        similarity_threshold: float = 0.85,
                        max_similar_per_group: int = 2) -> Dict[str, Any]:
        """
        Search for variables with enhanced semantic search
        
        Args:
            query: Natural language search query
            top_k: Number of results to return (default 50)
            use_semantic: Whether to use semantic search
            use_keyword: Whether to use keyword search
            filters: Optional filters
            use_advanced_processing: Whether to use advanced query processing
            filter_similar: Whether to filter similar variables
            similarity_threshold: Minimum similarity to consider variables as similar
            max_similar_per_group: Maximum number of similar variables to keep per group
            
        Returns:
            Search results with metadata
        """
        # Ensure components are initialized (lazy loading)
        initialization_successful = self._ensure_initialized()
        
        # If initialization failed, try basic fallback search
        if not initialization_successful:
            logger.warning("Enhanced search not available, using fallback search")
            return self._basic_parquet_search(query, top_k, filter_similar, 
                                            similarity_threshold, max_similar_per_group)
        
        # Optimize query if it's complex (4+ words)
        query_optimization = None
        if use_advanced_processing and self.query_optimizer and len(query.split()) >= 4:
            query_optimization = self.query_optimizer.optimize_query(query)
        
        if self.enhanced_search:
            # Use enhanced search V2 with advanced processing
            results = self.enhanced_search.search(
                query=query,
                top_k=top_k,
                use_semantic=use_semantic,
                use_keyword=use_keyword,
                filters=filters,
                use_advanced_processing=use_advanced_processing,
                filter_similar=filter_similar,
                similarity_threshold=similarity_threshold,
                max_similar_per_group=max_similar_per_group
            )
            
            # Add query optimization info if available
            if query_optimization:
                results['query_optimization'] = query_optimization
            
            return results
        elif self.variable_selector:
            # Fallback to basic search
            results = self.variable_selector.search(
                query=query,
                top_k=top_k,
                use_semantic=use_semantic,
                use_keyword=use_keyword
            )
            
            return {
                'results': results,
                'total_found': len(results),
                'query_context': {'original_query': query},
                'search_methods': {
                    'keyword': use_keyword,
                    'semantic': use_semantic
                }
            }
        else:
            # Final fallback to basic parquet search
            logger.warning("No search backend available, attempting final fallback")
            return self._basic_parquet_search(query, top_k, filter_similar,
                                            similarity_threshold, max_similar_per_group)
    
    def get_variable_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded variables"""
        if self.enhanced_search:
            themes = {}
            products = {}
            domains = {}
            
            for var in self.enhanced_search.variables:
                # Count themes
                theme = var.theme
                themes[theme] = themes.get(theme, 0) + 1
                
                # Count products
                product = var.product
                products[product] = products.get(product, 0) + 1
                
                # Count domains
                domain = var.domain
                domains[domain] = domains.get(domain, 0) + 1
            
            return {
                'total_variables': len(self.enhanced_search.variables),
                'themes': themes,
                'products': products,
                'domains': domains,
                'has_embeddings': hasattr(self.enhanced_search, 'faiss_index'),
                'search_config': {
                    'default_top_k': self.enhanced_search.config.default_top_k,
                    'hybrid_weights': {
                        'semantic': self.enhanced_search.config.hybrid_weight_semantic,
                        'keyword': self.enhanced_search.config.hybrid_weight_keyword
                    }
                }
            }
        elif self.variable_selector:
            return self.variable_selector.get_variable_stats()
        else:
            return {'error': 'No variables loaded'}
    
    def search_by_category(self, category: str, top_k: int = 50) -> List[Dict[str, Any]]:
        """Search variables by category"""
        if self.enhanced_search:
            # Filter by category
            results = []
            for var in self.enhanced_search.variables:
                if var.category and category.lower() in var.category.lower():
                    results.append(var.to_dict())
            
            # Sort by some relevance (e.g., description length)
            results.sort(key=lambda x: len(x.get('description', '')), reverse=True)
            
            return results[:top_k]
        elif self.variable_selector:
            return self.variable_selector.get_variables_by_category(category)[:top_k]
        else:
            return []
    
    def get_variable_by_id(self, var_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific variable by ID"""
        if self.enhanced_search and var_id in self.enhanced_search.variable_lookup:
            return self.enhanced_search.variable_lookup[var_id].to_dict()
        elif self.variable_selector:
            return self.variable_selector.get_variable_by_id(var_id)
        else:
            return None
    
    def get_concept_suggestions(self, query: str) -> Dict[str, Any]:
        """
        Get concept-based variable suggestions for complex queries
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with concept analysis and variable suggestions
        """
        if self.enhanced_search and hasattr(self.enhanced_search, 'get_concept_suggestions'):
            return self.enhanced_search.get_concept_suggestions(query)
        else:
            return {
                'error': 'Concept suggestions not available',
                'message': 'Enhanced search V2 required for concept analysis'
            }


# Flask API endpoints
def create_enhanced_variable_picker_blueprint(api_key: Optional[str] = None):
    """Create Flask blueprint for enhanced variable picker API"""
    from flask import Blueprint, request, jsonify
    
    bp = Blueprint('enhanced_variable_picker', __name__)
    
    # Initialize API
    picker_api = EnhancedVariablePickerAPI(openai_api_key=api_key)
    
    @bp.route('/search', methods=['POST'])
    def search_variables():
        """Search for variables"""
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 50)
        use_semantic = data.get('use_semantic', True)
        use_keyword = data.get('use_keyword', True)
        filters = data.get('filters', None)
        use_advanced_processing = data.get('use_advanced_processing', True)
        filter_similar = data.get('filter_similar', False)
        similarity_threshold = data.get('similarity_threshold', 0.85)
        max_similar_per_group = data.get('max_similar_per_group', 2)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = picker_api.search_variables(
            query=query,
            top_k=top_k,
            use_semantic=use_semantic,
            use_keyword=use_keyword,
            filters=filters,
            use_advanced_processing=use_advanced_processing,
            filter_similar=filter_similar,
            similarity_threshold=similarity_threshold,
            max_similar_per_group=max_similar_per_group
        )
        
        return jsonify(results)
    
    @bp.route('/stats', methods=['GET'])
    def get_stats():
        """Get variable statistics"""
        return jsonify(picker_api.get_variable_stats())
    
    @bp.route('/variable/<var_id>', methods=['GET'])
    def get_variable(var_id):
        """Get specific variable"""
        var = picker_api.get_variable_by_id(var_id)
        if var:
            return jsonify(var)
        else:
            return jsonify({'error': 'Variable not found'}), 404
    
    @bp.route('/category/<category>', methods=['GET'])
    def search_by_category(category):
        """Search by category"""
        top_k = request.args.get('top_k', 50, type=int)
        results = picker_api.search_by_category(category, top_k)
        return jsonify({
            'category': category,
            'results': results,
            'count': len(results)
        })
    
    @bp.route('/concepts/suggestions', methods=['POST'])
    def get_concept_suggestions():
        """Get concept-based variable suggestions"""
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        suggestions = picker_api.get_concept_suggestions(query)
        return jsonify(suggestions)
    
    return bp