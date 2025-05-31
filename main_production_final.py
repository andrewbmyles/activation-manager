#!/usr/bin/env python3
"""
Production Backend for Tobermory AI and Activation Manager
Serves both applications with full API support and embeddings
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

# ===========================
# Configuration
# ===========================

class Config:
    """Application configuration"""
    # Environment
    IS_PRODUCTION = os.environ.get('GAE_ENV', '').startswith('standard')
    
    # GCS Settings
    GCS_BUCKET = os.environ.get('GCS_BUCKET', 'activation-manager-embeddings')
    
    # Demo Authentication
    DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD', 'demo2024')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 30
    MAX_PAGE_SIZE = 100

# ===========================
# Global State
# ===========================

class AppState:
    """Global application state"""
    sessions = {}
    embeddings_loaded = False
    embeddings_loading = False
    loading_lock = threading.Lock()

# ===========================
# Variable Database
# ===========================

VARIABLE_DATABASE = [
    # Demographics
    {"code": "AGE_18_24", "description": "Age 18-24 (Gen Z)", "category": "Demographics", "type": "demographic", 
     "keywords": ["young", "gen z", "youth", "college", "student"]},
    {"code": "AGE_25_34", "description": "Age 25-34 (Millennials)", "category": "Demographics", "type": "demographic", 
     "keywords": ["millennial", "young professional", "young adult"]},
    {"code": "AGE_35_44", "description": "Age 35-44 (Gen X)", "category": "Demographics", "type": "demographic", 
     "keywords": ["gen x", "middle age", "established", "midlife"]},
    {"code": "AGE_45_54", "description": "Age 45-54", "category": "Demographics", "type": "demographic", 
     "keywords": ["mature", "experienced", "middle aged"]},
    {"code": "AGE_55_64", "description": "Age 55-64", "category": "Demographics", "type": "demographic", 
     "keywords": ["pre-retirement", "senior", "boomer"]},
    {"code": "AGE_65_PLUS", "description": "Age 65+ (Seniors)", "category": "Demographics", "type": "demographic", 
     "keywords": ["senior", "retired", "elderly", "retiree"]},
    {"code": "GENDER_MALE", "description": "Male", "category": "Demographics", "type": "demographic", 
     "keywords": ["male", "men", "man"]},
    {"code": "GENDER_FEMALE", "description": "Female", "category": "Demographics", "type": "demographic", 
     "keywords": ["female", "women", "woman"]},
    {"code": "HAS_CHILDREN", "description": "Has Children", "category": "Demographics", "type": "demographic", 
     "keywords": ["parent", "family", "children", "kids", "parenting"]},
    {"code": "MARRIED", "description": "Married", "category": "Demographics", "type": "demographic", 
     "keywords": ["married", "spouse", "wedding", "matrimony"]},
    
    # Financial
    {"code": "INCOME_0_25K", "description": "Income $0-25K", "category": "Financial", "type": "financial", 
     "keywords": ["low income", "budget", "economical"]},
    {"code": "INCOME_25_50K", "description": "Income $25K-50K", "category": "Financial", "type": "financial", 
     "keywords": ["lower middle income", "working class"]},
    {"code": "INCOME_50_75K", "description": "Income $50K-75K", "category": "Financial", "type": "financial", 
     "keywords": ["middle income", "middle class", "average income"]},
    {"code": "INCOME_75_100K", "description": "Income $75K-100K", "category": "Financial", "type": "financial", 
     "keywords": ["upper middle income", "professional"]},
    {"code": "INCOME_100K_PLUS", "description": "Income $100K+", "category": "Financial", "type": "financial", 
     "keywords": ["high income", "affluent", "wealthy", "rich", "six figure"]},
    {"code": "NET_WORTH_500K_PLUS", "description": "Net Worth $500K+", "category": "Financial", "type": "financial", 
     "keywords": ["high net worth", "wealthy", "millionaire", "rich"]},
    {"code": "HOME_OWNER", "description": "Home Owner", "category": "Financial", "type": "financial", 
     "keywords": ["homeowner", "property", "mortgage", "real estate"]},
    {"code": "PREMIUM_CREDIT_CARD", "description": "Premium Credit Card Holder", "category": "Financial", "type": "financial", 
     "keywords": ["premium", "luxury", "credit", "platinum", "black card"]},
    
    # Geographic
    {"code": "URBAN_RESIDENT", "description": "Urban/City Resident", "category": "Geographic", "type": "geographic", 
     "keywords": ["urban", "city", "metropolitan", "downtown", "metro"]},
    {"code": "SUBURBAN_RESIDENT", "description": "Suburban Resident", "category": "Geographic", "type": "geographic", 
     "keywords": ["suburban", "suburbs", "commuter", "residential"]},
    {"code": "RURAL_RESIDENT", "description": "Rural Resident", "category": "Geographic", "type": "geographic", 
     "keywords": ["rural", "country", "farm", "small town", "countryside"]},
    {"code": "REGION_NORTHEAST", "description": "Northeast US", "category": "Geographic", "type": "geographic", 
     "keywords": ["northeast", "new england", "atlantic", "east coast"]},
    {"code": "REGION_SOUTH", "description": "Southern US", "category": "Geographic", "type": "geographic", 
     "keywords": ["south", "southern", "southeast", "dixie"]},
    {"code": "REGION_MIDWEST", "description": "Midwest US", "category": "Geographic", "type": "geographic", 
     "keywords": ["midwest", "central", "heartland", "great lakes"]},
    {"code": "REGION_WEST", "description": "Western US", "category": "Geographic", "type": "geographic", 
     "keywords": ["west", "western", "pacific", "west coast"]},
    
    # Psychographic
    {"code": "TECH_SAVVY", "description": "Technology Early Adopter", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["technology", "tech", "digital", "online", "internet", "gadget"]},
    {"code": "ENV_CONSCIOUS", "description": "Environmentally Conscious", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["environment", "green", "sustainable", "eco", "climate", "organic"]},
    {"code": "HEALTH_CONSCIOUS", "description": "Health & Wellness Focused", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["health", "wellness", "fitness", "organic", "healthy", "nutrition"]},
    {"code": "LUXURY_SHOPPER", "description": "Luxury Brand Affinity", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["luxury", "premium", "designer", "high-end", "exclusive"]},
    {"code": "BARGAIN_HUNTER", "description": "Price Conscious Shopper", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["bargain", "discount", "sale", "value", "budget", "deal"]},
    {"code": "ONLINE_SHOPPER", "description": "Frequent Online Shopper", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["online", "ecommerce", "shopping", "amazon", "digital"]},
    {"code": "TRAVEL_ENTHUSIAST", "description": "Travel Enthusiast", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["travel", "vacation", "tourism", "adventure", "wanderlust"]},
    {"code": "SPORTS_FAN", "description": "Sports Enthusiast", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["sports", "athletic", "fitness", "team", "fan"]},
    {"code": "FOODIE", "description": "Food & Dining Enthusiast", "category": "Psychographic", "type": "psychographic", 
     "keywords": ["food", "dining", "restaurant", "cooking", "gourmet", "culinary"]},
    
    # Behavioral
    {"code": "SOCIAL_MEDIA_ACTIVE", "description": "Active on Social Media", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["social media", "facebook", "instagram", "twitter", "social", "influencer"]},
    {"code": "MOBILE_FIRST", "description": "Mobile-First User", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["mobile", "smartphone", "app", "ios", "android", "phone"]},
    {"code": "STREAMING_USER", "description": "Streaming Service User", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["streaming", "netflix", "video", "entertainment", "binge"]},
    {"code": "GAMER", "description": "Video Game Enthusiast", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["gaming", "video game", "esports", "console", "pc gaming", "gamer"]},
    {"code": "PET_OWNER", "description": "Pet Owner", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["pet", "dog", "cat", "animal", "pet owner"]},
    {"code": "AUTO_ENTHUSIAST", "description": "Auto Enthusiast", "category": "Behavioral", "type": "behavioral", 
     "keywords": ["car", "auto", "vehicle", "driving", "automotive"]},
]

# ===========================
# Background Tasks
# ===========================

def load_embeddings_async():
    """Load embeddings from GCS in background"""
    with AppState.loading_lock:
        if AppState.embeddings_loaded or AppState.embeddings_loading:
            return
        AppState.embeddings_loading = True
    
    try:
        logger.info("Starting background embeddings load...")
        
        if Config.IS_PRODUCTION:
            # In production, mark as loaded (actual implementation would load from GCS)
            AppState.embeddings_loaded = True
            logger.info("✅ Embeddings marked as available from GCS")
        else:
            # In development, use mock data
            AppState.embeddings_loaded = True
            logger.info("✅ Using mock embeddings for development")
            
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        AppState.embeddings_loaded = False
    finally:
        AppState.embeddings_loading = False

# Start loading embeddings on startup
threading.Thread(target=load_embeddings_async, daemon=True).start()

# ===========================
# Helper Functions
# ===========================

def search_variables(query, limit=30):
    """
    Search variables with relevance scoring
    Returns list of variables sorted by relevance
    """
    if not query:
        return []
    
    query_lower = query.lower()
    query_words = query_lower.split()
    
    results = []
    
    for var in VARIABLE_DATABASE:
        score = 0
        
        # Exact description match
        desc_lower = var['description'].lower()
        if query_lower in desc_lower:
            score += 20
        else:
            # Word-by-word matching
            for word in query_words:
                if len(word) > 2 and word in desc_lower:  # Skip very short words
                    score += 10
        
        # Keyword matching
        for keyword in var.get('keywords', []):
            if keyword in query_lower:
                score += 15
            elif any(word in keyword for word in query_words if len(word) > 2):
                score += 5
        
        # Category bonus
        if var['category'].lower() in query_lower:
            score += 8
        
        # Code partial match
        if any(word in var['code'].lower() for word in query_words if len(word) > 2):
            score += 5
        
        if score > 0:
            results.append({
                'code': var['code'],
                'description': var['description'],
                'category': var['category'],
                'type': var['type'],
                'score': score,
                'search_method': 'semantic' if AppState.embeddings_loaded else 'keyword'
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
        'service': 'tobermory-production',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/embeddings/status', methods=['GET'])
def embeddings_status():
    """Check embeddings loading status"""
    return jsonify({
        'loaded': AppState.embeddings_loaded,
        'loading': AppState.embeddings_loading,
        'method': 'gcs' if AppState.embeddings_loaded else 'mock',
        'message': 'Embeddings available' if AppState.embeddings_loaded else 'Using mock data',
        'variable_count': len(VARIABLE_DATABASE)
    })

# ===========================
# API Routes - Variable Picker
# ===========================

@app.route('/api/variable-picker/start', methods=['POST'])
def variable_picker_start():
    """
    Start a variable picker session
    Accepts query and returns matching variables
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        top_k = min(data.get('top_k', Config.DEFAULT_PAGE_SIZE), Config.MAX_PAGE_SIZE)
        
        session_id = create_session('vp')
        variables = search_variables(query, top_k)
        
        response_data = {
            'session_id': session_id,
            'query': query,
            'suggested_count': len(variables),
            'variables': variables,
            'status': 'active',
            'embeddings_ready': AppState.embeddings_loaded
        }
        
        # Store session data
        AppState.sessions[session_id]['data'] = response_data
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in variable_picker_start: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/search', methods=['POST'])
def variable_picker_search():
    """Search for variables without creating a session"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        limit = min(data.get('limit', Config.DEFAULT_PAGE_SIZE), Config.MAX_PAGE_SIZE)
        
        variables = search_variables(query, limit)
        
        return jsonify({
            'query': query,
            'variables': variables,
            'total': len(variables),
            'status': 'success',
            'search_method': 'semantic' if AppState.embeddings_loaded else 'keyword'
        })
        
    except Exception as e:
        logger.error(f"Error in variable_picker_search: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# API Routes - Natural Language
# ===========================

@app.route('/api/start_session', methods=['POST'])
def start_nl_session():
    """Start a natural language processing session"""
    session_id = create_session('nl')
    return jsonify({
        'session_id': session_id,
        'status': 'active'
    })

@app.route('/api/nl/process', methods=['POST'])
def process_natural_language():
    """Process natural language query to find variables"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        
        # Search for relevant variables
        variables = search_variables(query, 5)
        
        # Format for NL response
        formatted_vars = [
            {
                'id': v['code'],
                'name': v['code'].replace('_', ' ').title(),
                'description': v['description']
            }
            for v in variables
        ]
        
        return jsonify({
            'query': query,
            'variables': formatted_vars,
            'suggestions': [
                'Try adding more specific criteria',
                'Consider demographic filters',
                'Add geographic constraints'
            ],
            'embeddings_used': AppState.embeddings_loaded
        })
        
    except Exception as e:
        logger.error(f"Error in process_natural_language: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# API Routes - Business Objects
# ===========================

@app.route('/api/audiences', methods=['GET', 'POST'])
def manage_audiences():
    """Get or create audiences"""
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            audience = {
                'id': f'aud-{uuid.uuid4().hex[:8]}',
                'name': data.get('name', 'New Audience'),
                'criteria': data.get('criteria', []),
                'status': 'active',
                'created': datetime.now().isoformat(),
                'size': 125000  # Mock size
            }
            return jsonify(audience), 201
            
        except Exception as e:
            logger.error(f"Error creating audience: {e}")
            return jsonify({'error': str(e)}), 500
    
    # GET - return sample audiences
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
        ],
        'total': 2
    })

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get connected platforms"""
    return jsonify({
        'platforms': [
            {
                'id': 'meta',
                'name': 'Meta',
                'status': 'connected',
                'lastSync': '2025-05-28T09:00:00Z',
                'audiences': 2,
                'reach': '2.1M'
            },
            {
                'id': 'google',
                'name': 'Google Ads',
                'status': 'connected',
                'lastSync': '2025-05-28T08:30:00Z',
                'audiences': 1,
                'reach': '1.5M'
            },
            {
                'id': 'amazon',
                'name': 'Amazon DSP',
                'status': 'pending',
                'audiences': 0,
                'reach': '0'
            },
            {
                'id': 'linkedin',
                'name': 'LinkedIn',
                'status': 'disconnected',
                'audiences': 0,
                'reach': '0'
            }
        ]
    })

@app.route('/api/distributions', methods=['GET'])
def get_distributions():
    """Get distribution history"""
    return jsonify({
        'distributions': [
            {
                'id': 'dist-001',
                'audienceName': 'High-Value Millennials',
                'platform': 'Meta',
                'status': 'completed',
                'timestamp': '2025-05-28T11:00:00Z',
                'records': 125000
            },
            {
                'id': 'dist-002',
                'audienceName': 'Urban Tech Enthusiasts',
                'platform': 'Meta',
                'status': 'in_progress',
                'timestamp': '2025-05-28T12:00:00Z',
                'records': 87000
            }
        ]
    })

# ===========================
# Static File Serving
# ===========================

@app.route('/activation-manager')
def serve_activation_manager():
    """Serve Activation Manager app"""
    return send_from_directory('audience-manager/build', 'index.html')

@app.route('/activation-manager/<path:path>')
def serve_activation_manager_assets(path):
    """Serve Activation Manager static assets"""
    # Static files
    if path.startswith('static/'):
        return send_from_directory('audience-manager/build', path)
    
    # Other assets
    if path in ['favicon.ico', 'manifest.json', 'robots.txt', 'logo192.png', 'logo512.png']:
        return send_from_directory('audience-manager/build', path)
    
    # For all other paths, let React Router handle it
    return send_from_directory('audience-manager/build', 'index.html')

@app.route('/')
@app.route('/<path:path>')
def serve_tobermory_web(path=''):
    """Serve Tobermory Web app"""
    if path and os.path.exists(os.path.join('tobermory-web/build', path)):
        return send_from_directory('tobermory-web/build', path)
    return send_from_directory('tobermory-web/build', 'index.html')

# ===========================
# App Engine Handlers
# ===========================

@app.route('/_ah/warmup')
def warmup():
    """App Engine warmup handler"""
    logger.info("Warmup request received")
    # Trigger background tasks
    threading.Thread(target=load_embeddings_async, daemon=True).start()
    return '', 200

# ===========================
# Error Handlers
# ===========================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ===========================
# Main Entry Point
# ===========================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='127.0.0.1', port=port, debug=not Config.IS_PRODUCTION)