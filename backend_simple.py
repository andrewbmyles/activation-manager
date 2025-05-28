#!/usr/bin/env python3
"""
Simple Backend for Activation Manager - Quick Start Version
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

# Mock variable data for quick testing
MOCK_VARIABLES = [
    {"code": "AGE_25_34", "description": "Age 25-34", "category": "demographic"},
    {"code": "INCOME_100K", "description": "Income over $100k", "category": "financial"},
    {"code": "URBAN", "description": "Urban residents", "category": "geographic"},
    {"code": "TECH_SAVVY", "description": "Technology early adopters", "category": "behavioral"},
]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Simple backend running'
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
    """Process natural language query with mock data"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Simple keyword matching for demo
        results = []
        query_lower = query.lower()
        
        for var in MOCK_VARIABLES:
            if any(word in var['description'].lower() for word in query_lower.split()):
                results.append({
                    **var,
                    'score': 0.8,
                    'match_type': 'keyword'
                })
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results),
            'message': 'Using mock data for quick demo'
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable_picker/search', methods=['POST', 'OPTIONS'])
def search_variables():
    """Search variables with mock data"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    return process_nl_query()

@app.route('/api/variable-picker/start', methods=['POST', 'OPTIONS'])
def start_variable_picker():
    """Start variable picker session"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        # Create a session
        session_id = str(uuid.uuid4())
        
        # Simple keyword matching for demo
        results = []
        query_lower = query.lower()
        
        for var in MOCK_VARIABLES:
            if any(word in var['description'].lower() for word in query_lower.split()):
                results.append({
                    **var,
                    'score': 0.8,
                    'search_method': 'keyword'
                })
        
        return jsonify({
            'session_id': session_id,
            'query': query,
            'suggested_count': len(results),
            'variables': results,
            'status': 'completed'
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST', 'OPTIONS'])
def refine_variable_picker(session_id):
    """Refine variable picker search"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    # For demo, just return the same mock data
    return jsonify({
        'session_id': session_id,
        'status': 'completed',
        'variables': MOCK_VARIABLES,
        'suggested_count': len(MOCK_VARIABLES)
    })

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST', 'OPTIONS'])
def confirm_variables(session_id):
    """Confirm selected variables"""
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
    
    # For demo, return mock data
    if format_type == 'csv':
        return jsonify({
            'format': 'csv',
            'data': 'code,description,category\nAGE_25_34,Age 25-34,demographic\nINCOME_100K,Income over $100k,financial'
        })
    else:
        return jsonify({
            'format': 'json',
            'data': MOCK_VARIABLES
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting Simple Backend on port {port}")
    logger.info("📌 Using mock data for quick testing")
    app.run(host='0.0.0.0', port=port, debug=True)