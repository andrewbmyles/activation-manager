"""
Unified search API endpoint with migration support
"""
import logging
from flask import Blueprint, request, jsonify
from typing import Optional

from ..search import SearchConfig
from ..search.migration import get_migration_instance

logger = logging.getLogger(__name__)


def create_unified_search_blueprint(config: Optional[SearchConfig] = None):
    """Create Flask blueprint for unified search API with migration support"""
    
    bp = Blueprint('unified_search', __name__)
    
    # Get migration instance
    migration = get_migration_instance(config)
    
    @bp.route('/search', methods=['POST'])
    def search():
        """
        Unified search endpoint with A/B testing support
        
        Maintains backward compatibility with enhanced-variable-picker API
        """
        try:
            data = request.json or {}
            
            # Extract parameters
            query = data.get('query', '')
            top_k = data.get('top_k', 50)
            
            # Get user ID for consistent A/B routing (optional)
            user_id = request.headers.get('X-User-ID') or data.get('user_id')
            
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            # Log request for monitoring
            logger.info(f"🔍 Unified search request: query='{query[:50]}...', top_k={top_k}")
            
            # Use migration to route to appropriate implementation
            results = migration.search(
                query=query,
                top_k=top_k,
                user_id=user_id,
                **data  # Pass all other parameters
            )
            
            # Log which implementation was used
            implementation = results.get('_implementation', 'unknown')
            logger.info(f"📊 Search completed via {implementation}: {results.get('total_found', 0)} results")
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"Unified search error: {e}")
            return jsonify({
                'error': str(e),
                'results': [],
                'total_found': 0
            }), 500
    
    @bp.route('/stats', methods=['GET'])
    def stats():
        """Get unified search statistics including migration metrics"""
        try:
            from ..search import UnifiedSearch
            
            # Get search stats
            unified = UnifiedSearch.get_instance()
            stats = unified.get_stats()
            
            # Add migration metrics
            stats['migration'] = migration.get_metrics()
            
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/migration/status', methods=['GET'])
    def migration_status():
        """Get current migration status and metrics"""
        try:
            metrics = migration.get_metrics()
            config_dict = migration.config.to_dict()
            
            return jsonify({
                'enabled': migration.config.enable_ab_testing,
                'rollout_percentage': migration.config.unified_rollout_percentage,
                'metrics': metrics,
                'config': config_dict
            })
            
        except Exception as e:
            logger.error(f"Migration status error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/migration/rollout', methods=['POST'])
    def update_rollout():
        """Update rollout percentage (for testing/gradual rollout)"""
        try:
            data = request.json or {}
            new_percentage = data.get('percentage')
            
            if new_percentage is None:
                return jsonify({'error': 'percentage is required'}), 400
                
            if not 0 <= new_percentage <= 100:
                return jsonify({'error': 'percentage must be between 0 and 100'}), 400
            
            # Update config
            migration.config.unified_rollout_percentage = new_percentage
            
            # Enable A/B testing if percentage is between 0 and 100
            migration.config.enable_ab_testing = (0 < new_percentage < 100)
            
            logger.info(f"Updated unified search rollout to {new_percentage}%")
            
            return jsonify({
                'success': True,
                'rollout_percentage': new_percentage,
                'ab_testing_enabled': migration.config.enable_ab_testing
            })
            
        except Exception as e:
            logger.error(f"Rollout update error: {e}")
            return jsonify({'error': str(e)}), 500
    
    return bp