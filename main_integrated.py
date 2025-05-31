#!/usr/bin/env python3
"""
Integrated Backend for Tobermory AI
Serves both the main tobermory-web app and the Activation Manager
"""

import os
import sys
import json
import uuid
import time
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins='*', allow_headers='*', methods='*')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Parquet variable loader
try:
    from activation_manager.core.parquet_variable_loader import ParquetVariableLoader
    variable_loader = ParquetVariableLoader()
    logger.info(f"Loaded {len(variable_loader.get_all_variables())} variables from Parquet")
except Exception as e:
    logger.error(f"Failed to load Parquet variables: {e}")
    # Fallback to CSV loader
    try:
        from activation_manager.core.csv_variable_loader import CSVVariableLoader
        variable_loader = CSVVariableLoader()
        logger.info(f"Loaded {len(variable_loader.get_all_variables())} variables from CSV")
    except Exception as e2:
        logger.error(f"Failed to load variables: {e2}")
        variable_loader = None

# ===========================
# Configuration
# ===========================

class Config:
    """Application configuration"""
    # Environment
    IS_PRODUCTION = os.environ.get('GAE_ENV', '').startswith('standard')
    
    # GCS Settings
    GCS_BUCKET = os.environ.get('GCS_BUCKET', 'activation-manager-embeddings')
    USE_EMBEDDINGS = os.environ.get('USE_EMBEDDINGS', 'true').lower() == 'true'
    EMBEDDING_LOAD_STRATEGY = os.environ.get('EMBEDDING_LOAD_STRATEGY', 'lazy')
    
    # Frontend settings
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# ===========================
# Application State
# ===========================

class AppState:
    """Global application state"""
    embeddings_handler = None
    embeddings_loaded = False
    embeddings_available = False
    sessions = {}
    audiences = {}
    
    # Mock data
    mock_variables = [
        {"code": "PET_OWNER", "description": "Pet Owner", "category": "behavioral", "type": "boolean"},
        {"code": "TRAVEL_ENTHUSIAST", "description": "Travel Enthusiast", "category": "behavioral", "type": "boolean"},
        {"code": "FITNESS_ACTIVE", "description": "Fitness Active", "category": "behavioral", "type": "boolean"},
        {"code": "TECH_SAVVY", "description": "Tech Savvy", "category": "technographic", "type": "boolean"},
        {"code": "PARENT", "description": "Parent", "category": "demographic", "type": "boolean"}
    ]

# ===========================
# Embeddings Loading
# ===========================

def check_embeddings_availability():
    """Check if embeddings are available without loading them"""
    if not Config.USE_EMBEDDINGS:
        return False
    
    try:
        if Config.IS_PRODUCTION:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(Config.GCS_BUCKET)
            
            # Check for any .npy files
            blobs = list(bucket.list_blobs(prefix='embeddings/', max_results=1))
            exists = any(blob.name.endswith('.npy') for blob in blobs)
            
            if exists:
                logger.info("✅ Embeddings available in GCS")
                AppState.embeddings_available = True
                return True
            else:
                logger.warning("❌ No embeddings found in GCS")
                return False
        else:
            # Local development - check for parquet files
            embeddings_dir = os.path.join(os.path.dirname(__file__), 'data', 'embeddings')
            if os.path.exists(embeddings_dir):
                parquet_files = [f for f in os.listdir(embeddings_dir) if f.endswith('.parquet')]
                if parquet_files:
                    logger.info(f"✅ Found {len(parquet_files)} local parquet files")
                    AppState.embeddings_available = True
                    return True
            
            logger.warning("❌ No local embeddings found")
            return False
    except Exception as e:
        logger.error(f"Error checking embeddings availability: {e}")
        return False

def load_embeddings_background():
    """Load embeddings in background thread"""
    if not AppState.embeddings_available:
        logger.info("Embeddings not available, skipping background load")
        return
    
    try:
        logger.info("Starting background embeddings load...")
        from activation_manager.core.embeddings_handler import EmbeddingsHandler
        
        AppState.embeddings_handler = EmbeddingsHandler(
            use_gcs=Config.IS_PRODUCTION,
            gcs_bucket=Config.GCS_BUCKET if Config.IS_PRODUCTION else None
        )
        
        # Load embeddings
        AppState.embeddings_handler.load_embeddings()
        AppState.embeddings_loaded = True
        logger.info("✅ Embeddings loaded successfully in background")
        
    except Exception as e:
        logger.error(f"Failed to load embeddings in background: {e}")
        AppState.embeddings_loaded = False

# Check embeddings availability on startup
if Config.USE_EMBEDDINGS:
    logger.info("Checking embeddings availability...")
    AppState.embeddings_available = check_embeddings_availability()
    if AppState.embeddings_available:
        logger.info("✅ Embeddings marked as available from GCS")
    else:
        logger.info("❌ Embeddings not available")
else:
    logger.info("Embeddings disabled by configuration")

# ===========================
# Helper Functions
# ===========================

def search_with_embeddings(query, limit=30):
    """Search using embeddings if available"""
    if not AppState.embeddings_loaded or not AppState.embeddings_handler:
        return []
    
    try:
        results = AppState.embeddings_handler.search(query, top_k=limit)
        return [{
            'code': r['code'],
            'description': r['description'],
            'category': r.get('theme', 'demographic').lower(),
            'type': r.get('type', 'categorical'),
            'score': r.get('score', 0.5),
            'theme': r.get('theme', 'Demographic'),
            'search_method': 'semantic'
        } for r in results]
    except Exception as e:
        logger.error(f"Embeddings search failed: {e}")
        return []

def search_variables(query, limit=30):
    """Search for variables using Parquet data with fast pandas operations"""
    if not query or not variable_loader:
        return []
    
    # Use the optimized search method if available
    if hasattr(variable_loader, 'search'):
        results = variable_loader.search(query, limit)
        # Add search_method field
        for r in results:
            r['search_method'] = 'parquet'
        return results
    
    # Fallback to manual search for CSV loader
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    results = []
    
    for var in variable_loader.get_all_variables():
        # Calculate relevance score
        desc_lower = var.get('description', '').lower()
        code_lower = var.get('code', '').lower()
        
        # Exact matches get highest score
        score = 0
        if query_lower in desc_lower:
            score += 50
        if query_lower in code_lower:
            score += 30
        
        # Word matches
        desc_words = set(desc_lower.split())
        common_words = query_words.intersection(desc_words)
        score += len(common_words) * 10
        
        # Partial matches
        for word in query_words:
            if any(word in desc_word for desc_word in desc_words):
                score += 5
        
        if score > 0:
            results.append({
                'code': var.get('code', ''),
                'description': var.get('description', ''),
                'category': var.get('category', ''),
                'type': var.get('type', ''),
                'theme': var.get('theme', ''),
                'context': var.get('context', ''),
                'score': score,
                'search_method': 'keyword'
            })
    
    # Sort by score descending and limit results
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

def create_session(prefix='session'):
    """Create a new session with unique ID"""
    session_id = f'{prefix}-{uuid.uuid4().hex[:8]}'
    AppState.sessions[session_id] = {
        'id': session_id,
        'created': datetime.now().isoformat(),
        'status': 'active'
    }
    return session_id

# ===========================
# API Routes - Health & Status
# ===========================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'tobermory-integrated',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/embeddings/status', methods=['GET'])
def embeddings_status():
    """Get embeddings loading status"""
    return jsonify({
        'available': AppState.embeddings_available,
        'loaded': AppState.embeddings_loaded,
        'enabled': Config.USE_EMBEDDINGS,
        'strategy': Config.EMBEDDING_LOAD_STRATEGY
    })

# ===========================
# API Routes - Session Management
# ===========================

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    """Start a new NL session"""
    try:
        session_id = create_session('nl')
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'created': AppState.sessions[session_id]['created']
        })
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===========================
# API Routes - Natural Language
# ===========================

@app.route('/api/nl/process', methods=['POST'])
def process_natural_language():
    """Process natural language query to find variables"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        action = data.get('action', 'process')
        payload = data.get('payload', {})
        
        if action == 'process':
            query = payload.get('input', '')
            
            # Search for top 50 relevant variables
            all_variables = search_variables(query, 50)
            
            # Group variables by category
            suggested_variables = {
                'demographic': [],
                'behavioral': [],
                'psychographic': [],
                'geographic': [],
                'technographic': []
            }
            
            for var in all_variables:
                # Use theme from CSV for categorization
                theme = var.get('theme', '').lower()
                category = var.get('category', '').lower()
                
                # Map to our UI categories
                category_key = 'demographic'  # default
                
                if theme == 'behavioural' or 'behavior' in category:
                    category_key = 'behavioral'
                elif theme == 'psychographic' or 'psycho' in category:
                    category_key = 'psychographic'
                elif theme == 'demographic' or 'demog' in category:
                    category_key = 'demographic'
                elif 'geo' in category or 'location' in category:
                    category_key = 'geographic'
                elif 'tech' in category or 'digital' in category:
                    category_key = 'technographic'
                
                # Normalize score to 0-1 range (max possible score is ~100)
                normalized_score = min(var.get('score', 0) / 100.0, 1.0)
                
                suggested_variables[category_key].append({
                    'code': var['code'],
                    'description': var['description'],
                    'type': category_key,
                    'category': var.get('category', ''),
                    'theme': var.get('theme', 'Other'),
                    'context': var.get('context', ''),
                    'operators': ['equals', 'not_equals', 'in', 'not_in'],
                    'relevance_score': normalized_score
                })
            
            # Sort each category by relevance score
            for category in suggested_variables:
                suggested_variables[category].sort(
                    key=lambda x: x['relevance_score'], 
                    reverse=True
                )
            
            return jsonify({
                'status': 'variables_suggested',
                'message': f'Found {len(all_variables)} relevant variables',
                'suggested_variables': suggested_variables
            })
        
        return jsonify({'status': 'error', 'message': 'Unknown action'}), 400
        
    except Exception as e:
        logger.error(f"NL processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===========================
# API Routes - Audience Management
# ===========================

@app.route('/api/audiences', methods=['GET'])
def get_audiences():
    """Get all audiences"""
    audiences_list = [
        {
            **audience,
            'created': audience.get('created', datetime.now().isoformat()),
            'platforms': audience.get('platforms', [])
        }
        for audience in AppState.audiences.values()
    ]
    return jsonify(audiences_list)

@app.route('/api/audiences', methods=['POST'])
def create_audience():
    """Create a new audience"""
    try:
        data = request.get_json()
        audience_id = str(uuid.uuid4())
        
        audience = {
            'id': audience_id,
            'name': data.get('name', 'Untitled Audience'),
            'type': data.get('type', 'segment'),
            'criteria': data.get('criteria', []),
            'platforms': data.get('platforms', []),
            'size': data.get('size', 0),
            'status': 'draft',
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        
        AppState.audiences[audience_id] = audience
        
        return jsonify(audience), 201
    except Exception as e:
        logger.error(f"Failed to create audience: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audiences/<audience_id>', methods=['PUT'])
def update_audience(audience_id):
    """Update an audience"""
    try:
        if audience_id not in AppState.audiences:
            return jsonify({'error': 'Audience not found'}), 404
        
        data = request.get_json()
        audience = AppState.audiences[audience_id]
        
        # Update fields
        audience.update({
            'name': data.get('name', audience['name']),
            'type': data.get('type', audience['type']),
            'criteria': data.get('criteria', audience['criteria']),
            'platforms': data.get('platforms', audience['platforms']),
            'size': data.get('size', audience['size']),
            'status': data.get('status', audience['status']),
            'updated': datetime.now().isoformat()
        })
        
        return jsonify(audience)
    except Exception as e:
        logger.error(f"Failed to update audience: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audiences/<audience_id>', methods=['DELETE'])
def delete_audience(audience_id):
    """Delete an audience"""
    if audience_id in AppState.audiences:
        del AppState.audiences[audience_id]
        return '', 204
    return jsonify({'error': 'Audience not found'}), 404

# ===========================
# API Routes - Variable Search
# ===========================

@app.route('/api/variables/search', methods=['GET', 'POST'])
def search_variables_api():
    """Search for variables (keyword + semantic if available)"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '')
            limit = data.get('limit', 30)
        else:
            query = request.args.get('q', '')
            limit = int(request.args.get('limit', 30))
        
        # Try semantic search first if embeddings are loaded
        if AppState.embeddings_loaded:
            results = search_with_embeddings(query, limit)
            if results:
                return jsonify({
                    'variables': results,
                    'total': len(results),
                    'search_method': 'semantic'
                })
        
        # Fall back to keyword search
        variables = search_variables(query, limit)
        
        # If no variable data, use mock variables
        if not variables and not variable_loader:
            variables = [v for v in AppState.mock_variables 
                        if query.lower() in v['description'].lower()]
        
        return jsonify({
            'variables': variables,
            'total': len(variables),
            'search_method': 'keyword'
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# API Routes - Variable Picker
# ===========================

@app.route('/api/variable-picker/start', methods=['POST'])
def start_variable_picker():
    """Start a variable picker session with initial search"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        top_k = data.get('top_k', 30)
        
        session_id = create_session('vp')
        
        # Store query in session
        session = AppState.sessions[session_id]
        session['query'] = query
        
        # Perform initial search if query provided
        if query:
            results = search_variables(query, top_k)
            
            # Try semantic search if embeddings are loaded
            if AppState.embeddings_loaded:
                semantic_results = search_with_embeddings(query, top_k)
                if semantic_results:
                    # Merge results, preferring semantic
                    seen_codes = {r['code'] for r in semantic_results}
                    for result in results:
                        if result['code'] not in seen_codes:
                            semantic_results.append(result)
                    results = semantic_results[:top_k]
            
            session['initial_results'] = results
            
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'variables': results,
                'total': len(results)
            })
        else:
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'variables': [],
                'total': 0
            })
            
    except Exception as e:
        logger.error(f"Failed to start variable picker session: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST', 'OPTIONS'])
def refine_variable_picker(session_id):
    """Refine variable picker search"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        refinement = data.get('refinement', '')
        exclude_codes = data.get('exclude_codes', [])
        
        # Get the original session
        if session_id not in AppState.sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = AppState.sessions[session_id]
        
        # Get original query if stored
        original_query = session.get('query', '')
        
        # Combine original and refinement
        combined_query = f"{original_query} {refinement}".strip()
        
        logger.info(f"Refining search for session {session_id}: '{combined_query}'")
        
        # Search with combined query
        all_results = search_variables(combined_query, 50)
        
        # Try semantic search if embeddings are loaded
        if AppState.embeddings_loaded:
            semantic_results = search_with_embeddings(combined_query, 50)
            if semantic_results:
                # Merge results, preferring semantic
                seen_codes = {r['code'] for r in semantic_results}
                for result in all_results:
                    if result['code'] not in seen_codes:
                        semantic_results.append(result)
                all_results = semantic_results[:50]
        
        # Filter out excluded codes
        if exclude_codes:
            all_results = [r for r in all_results if r['code'] not in exclude_codes]
        
        # Take top 20 results
        refined_results = all_results[:20]
        
        # Update session
        session['query'] = combined_query
        session['refined_results'] = refined_results
        session['updated'] = datetime.now().isoformat()
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'variables': refined_results,
            'total': len(refined_results)
        })
        
    except Exception as e:
        logger.error(f"Failed to refine search: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST'])
def confirm_variable_picker(session_id):
    """Confirm selected variables"""
    try:
        if session_id not in AppState.sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        data = request.get_json() or {}
        selected_variables = data.get('variables', [])
        
        session = AppState.sessions[session_id]
        session['confirmed_variables'] = selected_variables
        session['status'] = 'confirmed'
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'confirmed_count': len(selected_variables)
        })
        
    except Exception as e:
        logger.error(f"Failed to confirm variables: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/variable-picker/export/<session_id>', methods=['GET'])
def export_variable_picker(session_id):
    """Export selected variables"""
    try:
        if session_id not in AppState.sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = AppState.sessions[session_id]
        confirmed_variables = session.get('confirmed_variables', [])
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'variables': confirmed_variables,
            'export_format': 'json'
        })
        
    except Exception as e:
        logger.error(f"Failed to export variables: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===========================
# Static File Serving
# ===========================

# Serve Tobermory Web (login/home) for root paths
@app.route('/')
@app.route('/login')
@app.route('/home')
def serve_tobermory_web():
    """Serve the Tobermory Web app"""
    return send_from_directory('tobermory-web/build', 'index.html')

# Serve Activation Manager for /activation-manager paths
@app.route('/activation-manager')
@app.route('/activation-manager/<path:path>')
def serve_activation_manager(path=''):
    """Serve the Activation Manager app"""
    # For the activation manager routes, we need to serve the audience-manager build
    return send_from_directory('audience-manager/build', 'index.html')

# Serve static files for Tobermory Web
@app.route('/static/<path:path>')
def serve_tobermory_static(path):
    """Serve static files based on the referer"""
    # Check if request is coming from activation manager
    referer = request.headers.get('Referer', '')
    if '/activation-manager' in referer:
        return send_from_directory('audience-manager/build/static', path)
    else:
        return send_from_directory('tobermory-web/build/static', path)

# Serve other static assets
@app.route('/<path:filename>')
def serve_static_file(filename):
    """Serve static files (images, manifest, etc.)"""
    # List of known static files
    static_files = ['favicon.ico', 'manifest.json', 'robots.txt', 
                   'logo192.png', 'logo512.png', 'headshot.jpg', 
                   'thetradedesk.png', 'tobermorylogo.png']
    
    if filename in static_files:
        # Try tobermory-web first
        tobermory_path = os.path.join('tobermory-web/build', filename)
        if os.path.exists(tobermory_path):
            return send_from_directory('tobermory-web/build', filename)
        
        # Then try audience-manager
        audience_path = os.path.join('audience-manager/build', filename)
        if os.path.exists(audience_path):
            return send_from_directory('audience-manager/build', filename)
    
    # Default to tobermory-web index
    return send_from_directory('tobermory-web/build', 'index.html')

# ===========================
# Warmup & Startup
# ===========================

@app.route('/_ah/warmup')
def warmup():
    """App Engine warmup handler"""
    logger.info("Warmup request received")
    
    # Start embeddings load if configured for eager loading
    if Config.USE_EMBEDDINGS and Config.EMBEDDING_LOAD_STRATEGY == 'eager':
        if not AppState.embeddings_loaded and AppState.embeddings_available:
            thread = threading.Thread(target=load_embeddings_background)
            thread.daemon = True
            thread.start()
    
    return '', 200

# ===========================
# Main Entry Point
# ===========================

# Load embeddings based on strategy
if Config.USE_EMBEDDINGS and AppState.embeddings_available:
    if Config.EMBEDDING_LOAD_STRATEGY == 'eager':
        # Load immediately in background
        logger.info("Starting eager embeddings load...")
        thread = threading.Thread(target=load_embeddings_background)
        thread.daemon = True
        thread.start()
    else:
        # Lazy loading - load on first request
        logger.info("Embeddings will be loaded on first request (lazy loading)")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting integrated server on port {port}")
    logger.info(f"Production mode: {Config.IS_PRODUCTION}")
    logger.info(f"Embeddings enabled: {Config.USE_EMBEDDINGS}")
    logger.info(f"Embeddings available: {AppState.embeddings_available}")
    logger.info(f"Variables loaded: {len(variable_loader.get_all_variables()) if variable_loader else 0}")
    
    app.run(host='0.0.0.0', port=port, debug=not Config.IS_PRODUCTION)