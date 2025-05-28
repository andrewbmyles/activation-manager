#!/usr/bin/env python3
"""
Unified Backend for Activation Manager
Supports both local development and GCP deployment
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# Add activation_manager to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from activation_manager.core.variable_selector import VariableSelector
from activation_manager.core.audience_builder import AudienceBuilder
from activation_manager.core.prizm_analyzer import PRIZMAnalyzer
from activation_manager.core.variable_picker_tool import VariablePickerTool
from activation_manager.core.embeddings_handler import EmbeddingsHandler
from activation_manager.config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS based on environment
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Production GCP environment
    CORS(app, origins=['https://activation-manager.appspot.com', 'https://*.appspot.com'])
else:
    # Local development
    CORS(app, origins='*', allow_headers='*', methods='*')

# Load configuration
settings = Settings()

# Initialize components
variable_selector = None
audience_builder = None
prizm_analyzer = None
variable_picker = None
embeddings_handler = None

# Session storage
sessions = {}

def initialize_components():
    """Initialize all components with proper error handling"""
    global variable_selector, audience_builder, prizm_analyzer, variable_picker, embeddings_handler
    
    try:
        logger.info("Initializing components...")
        
        # Initialize embeddings handler (optional - don't fail if missing)
        try:
            # Skip FAISS index build for faster startup
            embeddings_handler = EmbeddingsHandler(
                settings.embeddings_path,
                build_index=False  # Skip FAISS for faster startup
            )
            logger.info("✅ Embeddings handler initialized (without FAISS index)")
        except Exception as e:
            logger.warning(f"⚠️ Embeddings handler initialization failed: {str(e)}")
            embeddings_handler = None
        
        # Initialize variable selector with OpenAI key if available
        try:
            variable_selector = VariableSelector(
                openai_api_key=settings.openai_api_key
            )
            logger.info("✅ Variable selector initialized")
        except Exception as e:
            logger.warning(f"⚠️ Variable selector initialization failed: {str(e)}")
            variable_selector = None
        
        # Initialize other components
        # Create a variable catalog from loaded variables if available
        variable_catalog = {}
        if variable_selector and hasattr(variable_selector, 'variables'):
            variable_catalog = variable_selector.variables
        
        # Get data path from settings
        data_path = settings.get_variable_data_path()
        
        try:
            audience_builder = AudienceBuilder(variable_catalog, str(data_path)) if variable_catalog else None
            logger.info("✅ Audience builder initialized")
        except Exception as e:
            logger.warning(f"⚠️ Audience builder initialization failed: {str(e)}")
            audience_builder = None
            
        prizm_analyzer = PRIZMAnalyzer()
        
        # Only initialize variable picker if embeddings handler is available
        if embeddings_handler:
            variable_picker = VariablePickerTool(embeddings_handler)
        else:
            variable_picker = None
        
        logger.info("✅ Core components initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {str(e)}")
        raise

# Initialize components on startup
with app.app_context():
    initialize_components()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for GCP"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'variable_selector': variable_selector is not None,
            'audience_builder': audience_builder is not None,
            'prizm_analyzer': prizm_analyzer is not None,
            'variable_picker': variable_picker is not None,
            'embeddings_handler': embeddings_handler is not None
        }
    })

@app.route('/api/start_session', methods=['POST', 'OPTIONS'])
def start_session():
    """Start a new session"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().isoformat(),
        'history': []
    }
    
    return jsonify({
        'session_id': session_id,
        'message': 'Session started successfully'
    })

@app.route('/api/nl/process', methods=['POST', 'OPTIONS'])
def process_nl_query():
    """Process natural language query"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        session_id = data.get('session_id')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Log query
        logger.info(f"Processing query: {query}")
        
        # Process with variable selector
        results = variable_selector.search(
            query,
            top_k=10,
            use_semantic=True,
            use_keyword=True
        )
        
        # Update session history if provided
        if session_id and session_id in sessions:
            sessions[session_id]['history'].append({
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'results_count': len(results)
            })
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audience/build', methods=['POST', 'OPTIONS'])
def build_audience():
    """Build audience from criteria"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        criteria = data.get('criteria', [])
        name = data.get('name', 'Untitled Audience')
        
        # Build audience
        audience = audience_builder.build_audience(name, criteria)
        
        return jsonify({
            'status': 'success',
            'audience': audience
        })
        
    except Exception as e:
        logger.error(f"Error building audience: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prizm/analyze', methods=['POST', 'OPTIONS'])
def analyze_prizm():
    """Analyze PRIZM segments"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        segments = data.get('segments', [])
        
        # Analyze segments
        analysis = prizm_analyzer.analyze_segments(segments)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing PRIZM: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable_picker/search', methods=['POST', 'OPTIONS'])
def search_variables():
    """Search variables using embeddings"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        # Search with variable picker
        results = variable_picker.search(query, top_k=top_k)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching variables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/start', methods=['POST', 'OPTIONS'])
def start_variable_picker():
    """Start variable picker session with full dataset"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 30)
        
        # Create a session
        session_id = str(uuid.uuid4())
        
        # Search using variable selector (full dataset)
        if variable_selector:
            results = variable_selector.search(
                query,
                top_k=top_k,
                use_semantic=True,
                use_keyword=True
            )
            
            # Format results for variable picker UI
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'code': result.get('varid', result.get('code', '')),
                    'description': result.get('description', ''),
                    'category': result.get('category', ''),
                    'type': result.get('product', result.get('type', '')),
                    'score': result.get('score', 0),
                    'search_method': result.get('match_type', 'keyword'),
                    'keywords': result.get('keywords', [])
                })
        else:
            formatted_results = []
        
        # Store session
        sessions[session_id] = {
            'id': session_id,
            'query': query,
            'variables': formatted_results,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'session_id': session_id,
            'query': query,
            'suggested_count': len(formatted_results),
            'variables': formatted_results,
            'status': 'completed'
        })
        
    except Exception as e:
        logger.error(f"Error starting variable picker: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST', 'OPTIONS'])
def refine_variable_picker(session_id):
    """Refine variable picker search"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        refinement = data.get('refinement', '')
        
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get original query and combine with refinement
        original_query = sessions[session_id].get('query', '')
        combined_query = f"{original_query} {refinement}"
        
        # Search again with combined query
        if variable_selector:
            results = variable_selector.search(
                combined_query,
                top_k=30,
                use_semantic=True,
                use_keyword=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'code': result.get('varid', result.get('code', '')),
                    'description': result.get('description', ''),
                    'category': result.get('category', ''),
                    'type': result.get('product', result.get('type', '')),
                    'score': result.get('score', 0),
                    'search_method': result.get('match_type', 'keyword'),
                    'keywords': result.get('keywords', [])
                })
            
            # Update session
            sessions[session_id]['variables'] = formatted_results
            sessions[session_id]['refinement'] = refinement
        else:
            formatted_results = []
        
        return jsonify({
            'session_id': session_id,
            'status': 'completed',
            'variables': formatted_results,
            'suggested_count': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Error refining search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST', 'OPTIONS'])
def confirm_variables(session_id):
    """Confirm selected variables"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        confirmed_codes = data.get('confirmed_codes', [])
        
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Store confirmed codes
        sessions[session_id]['confirmed_codes'] = confirmed_codes
        
        return jsonify({
            'session_id': session_id,
            'status': 'confirmed',
            'confirmed_count': len(confirmed_codes),
            'confirmed_codes': confirmed_codes
        })
        
    except Exception as e:
        logger.error(f"Error confirming variables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/export/<session_id>', methods=['GET'])
def export_variables(session_id):
    """Export confirmed variables"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        format_type = request.args.get('format', 'json')
        session = sessions[session_id]
        variables = session.get('variables', [])
        confirmed_codes = session.get('confirmed_codes', [])
        
        # Filter to only confirmed variables
        confirmed_vars = [v for v in variables if v['code'] in confirmed_codes]
        
        if format_type == 'csv':
            # Generate CSV
            csv_lines = ['code,description,category,type,score']
            for var in confirmed_vars:
                csv_lines.append(f"{var['code']},{var['description']},{var['category']},{var['type']},{var['score']}")
            
            return jsonify({
                'format': 'csv',
                'data': '\n'.join(csv_lines)
            })
        else:
            return jsonify({
                'format': 'json',
                'data': confirmed_vars
            })
            
    except Exception as e:
        logger.error(f"Error exporting variables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<audience_id>', methods=['GET'])
def export_audience(audience_id):
    """Export audience data"""
    try:
        # Mock export for now - replace with actual implementation
        export_data = {
            'audience_id': audience_id,
            'exported_at': datetime.now().isoformat(),
            'format': request.args.get('format', 'json')
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        logger.error(f"Error exporting audience: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Main entry point"""
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Activation Manager Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

if __name__ == '__main__':
    main()