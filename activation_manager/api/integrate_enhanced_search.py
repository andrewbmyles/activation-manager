"""
Integration module for enhanced semantic search
This shows how to integrate the enhanced search into the existing Flask app
"""

import os
from flask import Flask, request, jsonify
from .enhanced_variable_picker_api import EnhancedVariablePickerAPI


def integrate_enhanced_search(app: Flask, openai_api_key: Optional[str] = None):
    """
    Integrate enhanced semantic search into existing Flask app
    
    Args:
        app: Flask application instance
        openai_api_key: OpenAI API key for semantic search
    """
    # Initialize enhanced API
    enhanced_api = EnhancedVariablePickerAPI(openai_api_key=openai_api_key)
    
    # Add enhanced search endpoint
    @app.route('/api/variables/enhanced-search', methods=['POST'])
    def enhanced_search():
        """Enhanced search endpoint with 50-result capability"""
        try:
            data = request.get_json()
            
            # Extract parameters
            query = data.get('query', '')
            top_k = data.get('top_k', 50)  # Default to 50 results
            use_semantic = data.get('use_semantic', True)
            use_keyword = data.get('use_keyword', True)
            filters = data.get('filters', None)
            
            if not query:
                return jsonify({
                    'error': 'Query is required',
                    'status': 'error'
                }), 400
            
            # Perform search
            results = enhanced_api.search_variables(
                query=query,
                top_k=top_k,
                use_semantic=use_semantic,
                use_keyword=use_keyword,
                filters=filters
            )
            
            # Add status for compatibility
            results['status'] = 'success'
            
            return jsonify(results)
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
    
    # Add variable stats endpoint
    @app.route('/api/variables/stats', methods=['GET'])
    def variable_stats():
        """Get variable statistics"""
        try:
            stats = enhanced_api.get_variable_stats()
            stats['status'] = 'success'
            return jsonify(stats)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
    
    # Add category search endpoint
    @app.route('/api/variables/category/<category>', methods=['GET'])
    def search_by_category(category):
        """Search variables by category"""
        try:
            top_k = request.args.get('top_k', 50, type=int)
            results = enhanced_api.search_by_category(category, top_k)
            
            return jsonify({
                'category': category,
                'results': results,
                'count': len(results),
                'status': 'success'
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
    
    # Add variable detail endpoint
    @app.route('/api/variables/<var_id>', methods=['GET'])
    def get_variable(var_id):
        """Get specific variable details"""
        try:
            var = enhanced_api.get_variable_by_id(var_id)
            if var:
                return jsonify({
                    'variable': var,
                    'status': 'success'
                })
            else:
                return jsonify({
                    'error': 'Variable not found',
                    'status': 'error'
                }), 404
        except Exception as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
    
    return enhanced_api


# Example usage in main Flask app
def update_main_flask_app():
    """
    Example of how to update the main Flask app to use enhanced search
    
    This would be added to your main.py or wherever your Flask app is initialized
    """
    
    # In your main Flask app file:
    """
    from activation_manager.api.integrate_enhanced_search import integrate_enhanced_search
    
    # After creating Flask app
    app = Flask(__name__)
    
    # ... other app configuration ...
    
    # Integrate enhanced search
    openai_key = os.getenv('OPENAI_API_KEY')
    enhanced_api = integrate_enhanced_search(app, openai_api_key=openai_key)
    
    # The enhanced search is now available at:
    # POST /api/variables/enhanced-search
    # GET  /api/variables/stats
    # GET  /api/variables/category/<category>
    # GET  /api/variables/<var_id>
    """
    pass


# Backward compatibility wrapper
def create_backward_compatible_search(enhanced_api: EnhancedVariablePickerAPI):
    """
    Create a search function that's backward compatible with existing code
    but uses the enhanced search underneath
    """
    def search_variables(query: str, top_k: int = 10, use_embeddings: bool = True):
        """
        Backward compatible search function
        
        Args:
            query: Search query
            top_k: Number of results (will be increased to minimum 50 internally)
            use_embeddings: Whether to use semantic search
            
        Returns:
            List of variable dictionaries
        """
        # Use enhanced search with minimum 50 results
        actual_top_k = max(top_k, 50)
        
        results = enhanced_api.search_variables(
            query=query,
            top_k=actual_top_k,
            use_semantic=use_embeddings,
            use_keyword=True
        )
        
        # Return just the results list for backward compatibility
        # But limit to requested top_k
        return results.get('results', [])[:top_k]
    
    return search_variables