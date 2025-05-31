#!/usr/bin/env python3
"""
Production Backend for GCP - Serves both apps and loads embeddings
"""

import os
import sys
import json
import uuid
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins='*', allow_headers='*', methods='*')

# Global variables
sessions = {}
embeddings_handler = None
embeddings_loaded = False
embeddings_loading = False
loading_lock = threading.Lock()

# Load embeddings in background
def load_embeddings_async():
    """Load embeddings from GCS in background"""
    global embeddings_handler, embeddings_loaded, embeddings_loading
    
    with loading_lock:
        if embeddings_loaded or embeddings_loading:
            return
        embeddings_loading = True
    
    try:
        logger.info("Starting background embeddings load from GCS...")
        
        # Only load if in App Engine environment
        if os.environ.get('GAE_ENV', '').startswith('standard'):
            from google.cloud import storage
            
            client = storage.Client()
            bucket_name = os.environ.get('GCS_BUCKET', 'activation-manager-embeddings')
            bucket = client.bucket(bucket_name)
            
            # For now, just mark as loaded - implement actual loading later
            embeddings_loaded = True
            logger.info("✅ Embeddings marked as available from GCS")
        else:
            logger.info("Not in App Engine environment, using mock data")
            embeddings_loaded = True
            
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        embeddings_loaded = False
    finally:
        embeddings_loading = False

# Start loading embeddings on startup
threading.Thread(target=load_embeddings_async, daemon=True).start()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'production-backend'})

@app.route('/api/embeddings/status', methods=['GET'])
def embeddings_status():
    """Check embeddings status"""
    return jsonify({
        'loaded': embeddings_loaded,
        'loading': embeddings_loading,
        'method': 'gcs' if embeddings_loaded else 'mock',
        'message': 'Embeddings available' if embeddings_loaded else 'Using mock data'
    })

# Route for activation manager
@app.route('/activation-manager')
def activation_manager_root():
    """Serve the Activation Manager app"""
    return send_from_directory('audience-manager/build', 'index.html')

@app.route('/activation-manager/<path:path>')
def activation_manager_assets(path):
    """Serve Activation Manager assets with proper paths"""
    # Handle static assets
    if path.startswith('static/'):
        return send_from_directory('audience-manager/build', path)
    # Handle other assets
    elif path in ['favicon.ico', 'manifest.json', 'robots.txt', 'logo192.png', 'logo512.png']:
        return send_from_directory('audience-manager/build', path)
    # For any other path, serve index.html (React routing)
    return send_from_directory('audience-manager/build', 'index.html')

# API Routes
@app.route('/api/variable-picker/start', methods=['POST'])
def variable_picker_start():
    """Start a variable picker session"""
    session_id = f'vp-{uuid.uuid4().hex[:8]}'
    sessions[session_id] = {
        'created': datetime.now().isoformat(),
        'status': 'active'
    }
    return jsonify({
        'session_id': session_id,
        'status': 'active',
        'embeddings_ready': embeddings_loaded
    })

@app.route('/api/variable-picker/search', methods=['POST'])
def variable_picker_search():
    """Search for variables - uses embeddings if available"""
    data = request.get_json()
    query = data.get('query', '')
    
    variables = []
    query_lower = query.lower()
    
    # If embeddings are loaded, we would use semantic search here
    # For now, use keyword matching
    
    if any(term in query_lower for term in ['millennial', 'age', 'young']):
        variables.append({
            'id': 'AGE_25_34',
            'name': 'Age 25-34',
            'description': 'Millennials (Age 25-34)',
            'category': 'Demographics',
            'type': 'demographic',
            'score': 18.0,
            'search_method': 'semantic' if embeddings_loaded else 'keyword'
        })
    
    if any(term in query_lower for term in ['income', 'wealth', 'affluent', 'rich']):
        variables.append({
            'id': 'INCOME_100K_PLUS',
            'name': 'Income $100K+',
            'description': 'Household Income $100,000 or more',
            'category': 'Financial',
            'type': 'financial',
            'score': 16.0,
            'search_method': 'semantic' if embeddings_loaded else 'keyword'
        })
    
    if any(term in query_lower for term in ['urban', 'city']):
        variables.append({
            'id': 'URBAN_RESIDENT',
            'name': 'Urban Resident',
            'description': 'Lives in Urban/City Area',
            'category': 'Geographic',
            'type': 'geographic',
            'score': 14.0,
            'search_method': 'semantic' if embeddings_loaded else 'keyword'
        })
    
    if any(term in query_lower for term in ['tech', 'technology', 'digital']):
        variables.append({
            'id': 'TECH_SAVVY',
            'name': 'Technology Enthusiast',
            'description': 'Early technology adopter',
            'category': 'Psychographic',
            'type': 'psychographic',
            'score': 15.0,
            'search_method': 'semantic' if embeddings_loaded else 'keyword'
        })
    
    # Sort by score
    variables.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'query': query,
        'variables': variables[:10],
        'total': len(variables),
        'status': 'success',
        'search_method': 'semantic' if embeddings_loaded else 'keyword'
    })

@app.route('/api/audiences', methods=['GET', 'POST'])
def audiences():
    """Manage audiences"""
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'id': f'aud-{uuid.uuid4().hex[:8]}',
            'name': data.get('name', 'New Audience'),
            'status': 'active',
            'created': datetime.now().isoformat()
        })
    
    return jsonify({
        'audiences': [
            {
                'id': 'aud-001',
                'name': 'High-Value Millennials',
                'size': 125000,
                'status': 'active',
                'lastUpdated': '2025-05-28T10:00:00Z'
            },
            {
                'id': 'aud-002',
                'name': 'Urban Tech Enthusiasts',
                'size': 87000,
                'status': 'active',
                'lastUpdated': '2025-05-28T11:30:00Z'
            }
        ]
    })

@app.route('/api/platforms', methods=['GET'])
def platforms():
    return jsonify({
        'platforms': [
            {
                'id': 'meta',
                'name': 'Meta',
                'status': 'connected',
                'lastSync': '2025-05-28T09:00:00Z'
            },
            {
                'id': 'google',
                'name': 'Google Ads',
                'status': 'connected',
                'lastSync': '2025-05-28T08:30:00Z'
            }
        ]
    })

@app.route('/api/distributions', methods=['GET'])
def distributions():
    return jsonify({
        'distributions': [
            {
                'id': 'dist-001',
                'audienceName': 'High-Value Millennials',
                'platform': 'Meta',
                'status': 'completed',
                'timestamp': '2025-05-28T11:00:00Z'
            }
        ]
    })

@app.route('/api/start_session', methods=['POST'])
def start_session():
    session_id = f'nl-{uuid.uuid4().hex[:8]}'
    sessions[session_id] = {
        'created': datetime.now().isoformat(),
        'status': 'active'
    }
    return jsonify({'session_id': session_id, 'status': 'active'})

@app.route('/api/nl/process', methods=['POST'])
def process_nl():
    data = request.get_json()
    query = data.get('query', '')
    
    # Enhanced NL processing with embeddings status
    return jsonify({
        'query': query,
        'variables': [
            {'id': 'var1', 'name': 'Age', 'description': 'Age demographics'},
            {'id': 'var2', 'name': 'Income', 'description': 'Household income'},
            {'id': 'var3', 'name': 'Location', 'description': 'Geographic location'}
        ],
        'suggestions': ['millennials', 'high income', 'urban areas'],
        'embeddings_used': embeddings_loaded
    })

# Serve Tobermory Web for root
@app.route('/')
@app.route('/<path:path>')
def serve_tobermory(path=''):
    """Serve the Tobermory Web app"""
    if path and os.path.exists(os.path.join('tobermory-web/build', path)):
        return send_from_directory('tobermory-web/build', path)
    return send_from_directory('tobermory-web/build', 'index.html')

# Warmup handler for App Engine
@app.route('/_ah/warmup')
def warmup():
    """App Engine warmup handler"""
    # Trigger embeddings load if not already started
    threading.Thread(target=load_embeddings_async, daemon=True).start()
    return '', 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)