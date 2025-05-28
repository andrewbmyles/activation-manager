#!/usr/bin/env python3
"""
GCP-optimized Backend for Activation Manager
Works without large embedding files
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins='*', allow_headers='*', methods='*')

# Session storage
sessions = {}

# Load variables from JSON (without embeddings for now)
VARIABLES = []
try:
    # Try to load from variables_full.json
    vars_path = os.path.join('activation_manager', 'data', 'embeddings', 'variables_full.json')
    if os.path.exists(vars_path):
        with open(vars_path, 'r') as f:
            vars_data = json.load(f)
            for var_id, var_info in vars_data.items():
                VARIABLES.append({
                    'code': var_info.get('varid', var_id),
                    'description': var_info.get('description', ''),
                    'category': var_info.get('category', ''),
                    'type': var_info.get('product', ''),
                    'keywords': var_info.get('keywords', [])
                })
        logger.info(f"✅ Loaded {len(VARIABLES)} variables from JSON")
    else:
        logger.warning("⚠️ No variables file found, using empty dataset")
except Exception as e:
    logger.error(f"Error loading variables: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'variables_loaded': len(VARIABLES),
        'message': 'GCP Backend running'
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
    """Process natural language query with simple search"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '').lower()
        
        # Simple keyword matching
        results = []
        for var in VARIABLES:
            score = 0
            desc_lower = var['description'].lower()
            keywords = ' '.join(var.get('keywords', [])).lower()
            
            # Check each word in query
            for word in query.split():
                if len(word) > 2:  # Skip short words
                    if word in desc_lower:
                        score += 2
                    if word in keywords:
                        score += 1
                    if word in var['category'].lower():
                        score += 1
            
            if score > 0:
                results.append({
                    **var,
                    'score': score / 10.0,  # Normalize score
                    'match_type': 'keyword'
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results[:30],
            'count': len(results[:30])
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/start', methods=['POST', 'OPTIONS'])
def start_variable_picker():
    """Start variable picker session"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    # Reuse the nl/process logic
    return process_nl_query()

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST', 'OPTIONS'])
def refine_variable_picker(session_id):
    """Refine search"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    # For now, just return empty results
    return jsonify({
        'session_id': session_id,
        'status': 'completed',
        'variables': [],
        'suggested_count': 0
    })

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST', 'OPTIONS'])
def confirm_variables(session_id):
    """Confirm variables"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    data = request.get_json()
    confirmed_codes = data.get('confirmed_codes', [])
    
    return jsonify({
        'session_id': session_id,
        'status': 'confirmed',
        'confirmed_count': len(confirmed_codes),
        'confirmed_codes': confirmed_codes
    })

@app.route('/api/variable-picker/export/<session_id>', methods=['GET'])
def export_variables(session_id):
    """Export variables"""
    format_type = request.args.get('format', 'json')
    
    return jsonify({
        'format': format_type,
        'data': []
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting GCP Backend on port {port}")
    logger.info(f"📊 Loaded {len(VARIABLES)} variables")
    app.run(host='0.0.0.0', port=port, debug=False)