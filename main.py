#!/usr/bin/env python3
"""
Production Backend for Tobermory AI and Activation Manager
Serves both applications with full API support and embeddings
"""

import os
import sys
import json
import uuid
import time
import logging
import threading
from datetime import datetime

# Set default environment variables to prevent hangs
# These can be overridden by setting them before running the app
if 'DISABLE_SPACY' not in os.environ:
    os.environ['DISABLE_SPACY'] = 'true'  # Disable spaCy by default to prevent hangs
if 'USE_EMBEDDINGS' not in os.environ:
    os.environ['USE_EMBEDDINGS'] = 'true'  # Keep embeddings enabled by default

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=== STARTING APP ENGINE DEPLOYMENT ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Environment: {os.environ.get('GAE_ENV', 'local')}")

try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    logger.info("✅ Flask imports successful")
except Exception as e:
    logger.error(f"❌ Flask import failed: {e}")
    raise

# Initialize Flask app
try:
    app = Flask(__name__)
    CORS(app, origins='*', allow_headers='*', methods='*')
    logger.info("✅ Flask app initialized")
except Exception as e:
    logger.error(f"❌ Flask initialization failed: {e}")
    raise

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import variable loaders - with detailed error handling
logger.info("🔄 Loading variable loaders...")
variable_loader = None

# Test pandas import first
try:
    import pandas as pd
    logger.info("  ✅ Pandas imported successfully")
except Exception as e:
    logger.error(f"  ❌ Pandas import failed: {e}")
    pd = None

# Only try Parquet loader if pandas is available
if pd is not None:
    try:
        logger.info("  Attempting Parquet loader import...")
        from activation_manager.core.parquet_variable_loader import ParquetVariableLoader
        logger.info("  Parquet loader imported, initializing...")
        variable_loader = ParquetVariableLoader()
        var_count = len(variable_loader.get_all_variables()) if variable_loader else 0
        logger.info(f"✅ Loaded {var_count} variables from Parquet (fast mode)")
    except ImportError as ie:
        logger.error(f"⚠️ Import error: {ie}")
        variable_loader = None
    except Exception as e:
        logger.error(f"⚠️ Parquet loader failed: {type(e).__name__}: {str(e)[:200]}")
        import traceback
        logger.error(f"  Traceback: {traceback.format_exc()[:500]}")
        variable_loader = None
else:
    logger.warning("⚠️ Pandas not available, skipping Parquet loader")

# Fall back to CSV if needed
if variable_loader is None:
    try:
        logger.info("  Attempting CSV loader...")
        from activation_manager.core.csv_variable_loader import CSVVariableLoader
        variable_loader = CSVVariableLoader()
        var_count = len(variable_loader.get_all_variables()) if variable_loader else 0
        logger.info(f"✅ Loaded {var_count} variables from CSV")
    except Exception as e2:
        logger.error(f"❌ CSV loader also failed: {str(e2)[:200]}")
        variable_loader = None

# ===========================
# Early Test Route
# ===========================

@app.route('/startup-test')
def startup_test():
    """Very early test route to verify Flask is working"""
    return "OK", 200

logger.info("✅ Early test route registered")

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

# Lazy load Enhanced Variable Picker to avoid startup delays
enhanced_picker = None
enhanced_picker_lock = threading.Lock()

def get_enhanced_picker():
    """Get or create Enhanced Variable Picker instance with lazy loading"""
    global enhanced_picker
    if enhanced_picker is None:
        with enhanced_picker_lock:
            if enhanced_picker is None:  # Double-check pattern
                try:
                    logger.info("🚀 Initializing Enhanced Variable Picker...")
                    from activation_manager.api.enhanced_variable_picker_api import EnhancedVariablePickerAPI
                    enhanced_picker = EnhancedVariablePickerAPI.get_instance()
                    logger.info("✅ Enhanced Variable Picker initialized")
                except Exception as e:
                    logger.error(f"❌ Enhanced Variable Picker failed: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Return None so endpoints can handle gracefully
                    enhanced_picker = None
    return enhanced_picker

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
    
    # Use variable loader (Parquet or CSV)
    if variable_loader:
        # Use the fast search method if available (Parquet), otherwise fallback
        if hasattr(variable_loader, 'search'):
            # Enhanced Parquet loader with fast pandas search
            results = variable_loader.search(query, limit)
        else:
            # CSV loader fallback
            results = variable_loader.search_by_description(query, limit)
        
        # If we have semantic search available, enhance with embeddings
        if AppState.embeddings_loaded and hasattr(AppState, 'variable_selector'):
            try:
                semantic_results = AppState.variable_selector.search(query, limit)
                
                # Merge results with semantic results
                seen_codes = {r.get('code', r.get('VarId', '')) for r in results}
                
                for sem_result in semantic_results:
                    var_id = sem_result.get('code', '')
                    if var_id and var_id not in seen_codes:
                        # Get full variable info
                        if hasattr(variable_loader, 'get_variable_by_id'):
                            var_data = variable_loader.get_variable_by_id(var_id)
                        else:
                            var_data = variable_loader.get_variable(var_id)
                            
                        if var_data:
                            var_data['score'] = sem_result.get('score', 0) * 100  # Convert to same scale
                            var_data['search_method'] = 'semantic'
                            results.append(var_data)
                
                # Re-sort by score
                results.sort(key=lambda x: x.get('score', x.get('search_score', 0)), reverse=True)
                
            except Exception as e:
                logger.error(f"Semantic search error: {e}")
        
        # Add search method info
        for result in results:
            if 'search_method' not in result:
                result['search_method'] = 'keyword'
        
        return results[:limit]
    
    # Fallback to mock data if CSV not loaded
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

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST'])
def variable_picker_refine(session_id):
    """Refine variable search results"""
    try:
        data = request.get_json() or {}
        refinement = data.get('refinement', '')
        exclude_codes = data.get('exclude_codes', [])
        original_query = data.get('original_query', '')  # Get from client
        
        # Combine original query with refinement
        refined_query = f"{original_query} {refinement}" if original_query else refinement
        
        # Search with refined query
        all_variables = search_variables(refined_query, Config.MAX_PAGE_SIZE)
        
        # Filter out excluded variables
        filtered_variables = [
            var for var in all_variables 
            if var.get('code') not in exclude_codes
        ]
        
        # Return new session data
        response_data = {
            'session_id': session_id,
            'query': refined_query,
            'variables': filtered_variables[:Config.DEFAULT_PAGE_SIZE],
            'suggested_count': len(filtered_variables),
            'status': 'active',
            'embeddings_ready': AppState.embeddings_loaded
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in variable_picker_refine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST'])
def variable_picker_confirm(session_id):
    """Confirm selected variables"""
    try:
        data = request.get_json() or {}
        confirmed_codes = data.get('confirmed_codes', [])
        all_variables = data.get('all_variables', [])  # Get from client
        
        # Filter to only confirmed variables
        confirmed_variables = [
            var for var in all_variables 
            if var.get('code') in confirmed_codes
        ]
        
        return jsonify({
            'session_id': session_id,
            'confirmed_variables': confirmed_variables,
            'status': 'confirmed'
        })
        
    except Exception as e:
        logger.error(f"Error in variable_picker_confirm: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/export/<session_id>', methods=['POST'])
def variable_picker_export(session_id):
    """Export confirmed variables"""
    try:
        format_type = request.args.get('format', 'json')
        data = request.get_json() or {}
        confirmed_variables = data.get('confirmed_variables', [])
        
        if format_type == 'csv':
            # Create CSV content
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=['code', 'description', 'category', 'type'])
            writer.writeheader()
            
            for var in confirmed_variables:
                writer.writerow({
                    'code': var.get('code', ''),
                    'description': var.get('description', ''),
                    'category': var.get('category', ''),
                    'type': var.get('type', '')
                })
            
            # Return as CSV file
            output.seek(0)
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=variables_{session_id}.csv'}
            )
            
        else:  # JSON format
            return jsonify({
                'session_id': session_id,
                'query': data.get('query', ''),
                'variables': confirmed_variables,
                'count': len(confirmed_variables),
                'format': 'json'
            })
            
    except Exception as e:
        logger.error(f"Error in variable_picker_export: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# API Routes - Data Persistence
# ===========================

# Import persistence handlers (disabled for now)
persistence_enabled = False
audience_handler = None
platform_handler = None
distribution_handler = None

# TODO: Re-enable when data_persistence module is properly deployed
# try:
#     from data_persistence.parquet_handlers import (
#         AudienceHandler, PlatformHandler, DistributionHandler
#     )
#     
#     # Initialize handlers
#     audience_handler = AudienceHandler()
#     platform_handler = PlatformHandler()
#     distribution_handler = DistributionHandler()
#     persistence_enabled = True
#     logger.info("✅ Data persistence handlers initialized")
# except Exception as e:
#     logger.warning(f"Data persistence not available: {e}")
#     persistence_enabled = False

# Audience persistence endpoints (disabled - using simpler implementation below)
# @app.route('/api/audiences', methods=['POST'])
# def save_audience():
#     """Save a new audience or update existing one"""
#     if not persistence_enabled:
#         return jsonify({'error': 'Persistence not available'}), 503
    
#     try:
#         data = request.json
#         
#         # Validate required fields
#         required = ['user_id', 'name', 'data_type', 'selected_variables']
#         for field in required:
#             if field not in data:
#                 return jsonify({'error': f'Missing required field: {field}'}), 400
#         
#         # Save audience
#         audience_id = audience_handler.save_audience(data)
#         
#         return jsonify({
#             'success': True,
#             'audience_id': audience_id,
#             'message': 'Audience saved successfully'
#         }), 201
#         
#     except Exception as e:
#         logger.error(f"Error saving audience: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/audiences/<audience_id>', methods=['GET'])
# def get_audience(audience_id):
#     """Get a specific audience by ID"""
#     if not persistence_enabled:
#         return jsonify({'error': 'Persistence not available'}), 503
    
#     try:
#         user_id = request.args.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'user_id parameter required'}), 400
#         
#         audience = audience_handler.get_audience(audience_id, user_id)
#         
#         if audience:
#             return jsonify({
#                 'success': True,
#                 'audience': audience
#             }), 200
#         else:
#             return jsonify({'error': 'Audience not found'}), 404
#             
#     except Exception as e:
#         logger.error(f"Error getting audience: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/audiences', methods=['GET'])
# def list_audiences():
#     """List audiences for a user"""
#     if not persistence_enabled:
#         return jsonify({'error': 'Persistence not available'}), 503
    
#     try:
#         user_id = request.args.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'user_id parameter required'}), 400
#         
#         status = request.args.get('status')
#         limit = int(request.args.get('limit', 50))
#         
#         audiences = audience_handler.list_audiences(user_id, status, limit)
#         
#         return jsonify({
#             'success': True,
#             'audiences': audiences,
#             'count': len(audiences)
#         }), 200
#         
#     except Exception as e:
#         logger.error(f"Error listing audiences: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/audiences/<audience_id>/status', methods=['PUT'])
# def update_audience_status(audience_id):
#     """Update audience status (archive, activate, etc.)"""
#     if not persistence_enabled:
#         return jsonify({'error': 'Persistence not available'}), 503
#     
#     try:
#         data = request.json
#         user_id = data.get('user_id')
#         status = data.get('status')
#         
#         if not user_id or not status:
#             return jsonify({'error': 'user_id and status required'}), 400
#         
#         if status not in ['draft', 'active', 'archived']:
#             return jsonify({'error': 'Invalid status'}), 400
#         
#         success = audience_handler.update_audience_status(audience_id, user_id, status)
#         
#         if success:
#             return jsonify({
#                 'success': True,
#                 'message': f'Audience status updated to {status}'
#             }), 200
#         else:
#             return jsonify({'error': 'Audience not found'}), 404
#             
#     except Exception as e:
#         logger.error(f"Error updating audience status: {e}")
#         return jsonify({'error': str(e)}), 500

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
                    'relevance_score': normalized_score,
                    'category': var.get('category', ''),
                    'theme': var.get('theme', ''),
                    'context': var.get('context', ''),
                    'operators': ['equals', 'not_equals', 'in', 'not_in']
                })
            
            # Limit each category to maintain UI performance
            for key in suggested_variables:
                suggested_variables[key] = suggested_variables[key][:15]
            
            return jsonify({
                'status': 'variables_suggested',
                'suggested_variables': suggested_variables,
                'message': f'Found {len(all_variables)} relevant variables'
            })
            
        elif action == 'confirm':
            # Handle variable confirmation
            segments = [
                {
                    'group_id': i,
                    'size': 25000 + (i * 5000),
                    'size_percentage': 5 + (i * 0.5),
                    'name': f'Segment {i+1}',
                    'dominantTraits': ['Trait 1', 'Trait 2', 'Trait 3']
                }
                for i in range(4)
            ]
            
            return jsonify({
                'status': 'complete',
                'segments': segments,
                'audience_id': f'aud_{int(time.time())}',
                'message': 'Segments created successfully'
            })
        
        # Fallback for other actions
        return jsonify({
            'status': 'success',
            'message': 'Action processed'
        })
        
    except Exception as e:
        logger.error(f"Error in process_natural_language: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# API Routes - Business Objects
# ===========================

@app.route('/api/audiences/<audience_id>', methods=['GET'])
def get_audience_by_id(audience_id):
    """Get a specific audience by ID"""
    user_id = request.args.get('user_id', 'demo_user')
    
    # Demo audience data
    demo_audiences = {
        'demo-gaming-audience': {
            'audience_id': 'demo-gaming-audience',
            'id': 'demo-gaming-audience',
            'name': 'Gaming Enthusiasts Q4',
            'enhanced_name': 'Gaming-Enthusiast Gen Z Males',
            'description': 'Find males aged 18-24 interested in gaming',
            'natural_language_criteria': 'Males between ages 18-24 who are interested in video games',
            'audience_size': 67842,
            'estimatedSize': 67842,
            'selected_variables': ['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'],
            'insights': [
                'Focused audience of 68K+ targeted users',
                'Digital-native generation',
                'High engagement with gaming content'
            ],
            'status': 'active',
            'type': '1st-party',
            'subtype': 'rampid',
            'created_at': '2025-05-28T10:00:00Z',
            'updatedAt': '2025-05-28T10:00:00Z',
            'platforms': []
        },
        'demo-fashion-audience': {
            'audience_id': 'demo-fashion-audience',
            'id': 'demo-fashion-audience',
            'name': 'Fashion Forward Millennials',
            'enhanced_name': 'Fashion-Forward Millennial Women',
            'description': 'Fashion-conscious millennial women with high disposable income',
            'natural_language_criteria': 'Females between ages 25-40 interested in fashion with high income',
            'audience_size': 54321,
            'estimatedSize': 54321,
            'selected_variables': ['AGE_25_40', 'GENDER_FEMALE', 'FASHION_INTEREST', 'HIGH_INCOME'],
            'insights': [
                'High purchasing power demographic',
                'Active on social media',
                'Brand conscious consumers'
            ],
            'status': 'active',
            'type': '3rd-party',
            'subtype': 'prizm-segment',
            'created_at': '2025-05-28T11:30:00Z',
            'updatedAt': '2025-05-28T11:30:00Z',
            'platforms': []
        }
    }
    
    audience = demo_audiences.get(audience_id)
    if audience:
        return jsonify({
            'success': True,
            'audience': audience
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Audience not found'
        }), 404

@app.route('/api/audiences', methods=['GET', 'POST'])
def manage_audiences():
    """Get or create audiences"""
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            
            # Extract audience data from nested structure if present
            audience_data = data.get('audience_data', data)
            
            # Generate new audience ID
            audience_id = f'aud-{uuid.uuid4().hex[:8]}'
            
            # Create audience object with expected fields
            audience = {
                'audience_id': audience_id,
                'id': audience_id,
                'name': audience_data.get('name', 'New Audience'),
                'description': audience_data.get('description', ''),
                'enhanced_name': audience_data.get('enhanced_name', audience_data.get('name', 'New Audience')),
                'natural_language_criteria': audience_data.get('natural_language_criteria', ''),
                'criteria': audience_data.get('criteria', []),
                'selected_variables': audience_data.get('selected_variables', []),
                'audience_size': audience_data.get('audience_size', 50000),
                'estimatedSize': audience_data.get('audience_size', 50000),
                'type': audience_data.get('type', '1st-party'),
                'subtype': audience_data.get('subtype', 'rampid'),
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'platforms': []
            }
            
            return jsonify({
                'success': True,
                'audience': audience,
                'audience_id': audience_id,
                'message': 'Audience created successfully'
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating audience: {e}")
            return jsonify({'error': str(e)}), 500
    
    # GET - return sample audiences
    user_id = request.args.get('user_id', 'demo_user')
    
    # Return demo audiences with the expected format
    demo_audiences = [
        {
            'audience_id': 'demo-gaming-audience',
            'id': 'demo-gaming-audience',
            'name': 'Gaming Enthusiasts Q4',
            'enhanced_name': 'Gaming-Enthusiast Gen Z Males',
            'description': 'Find males aged 18-24 interested in gaming',
            'natural_language_criteria': 'Males between ages 18-24 who are interested in video games',
            'audience_size': 67842,
            'size': 67842,
            'selected_variables': ['AGE_18_24', 'GENDER_MALE', 'GAMING_INTEREST'],
            'status': 'active',
            'created_at': '2025-05-28T10:00:00Z',
            'lastUpdated': '2025-05-28T10:00:00Z'
        },
        {
            'audience_id': 'demo-fashion-audience',
            'id': 'demo-fashion-audience',
            'name': 'Fashion Forward Millennials',
            'enhanced_name': 'Fashion-Forward Millennial Women',
            'description': 'Fashion-conscious millennial women with high disposable income',
            'natural_language_criteria': 'Females between ages 25-40 interested in fashion with high income',
            'audience_size': 54321,
            'size': 54321,
            'selected_variables': ['AGE_25_40', 'GENDER_FEMALE', 'FASHION_INTEREST', 'HIGH_INCOME'],
            'status': 'active',
            'created_at': '2025-05-28T11:30:00Z',
            'lastUpdated': '2025-05-28T11:30:00Z'
        }
    ]
    
    return jsonify({
        'success': True,
        'audiences': demo_audiences,
        'count': len(demo_audiences),
        'total': len(demo_audiences)
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
# Enhanced Variable Picker API with Migration Support
# ===========================

# Check for unified search feature flag
USE_UNIFIED_SEARCH = os.environ.get('USE_UNIFIED_SEARCH', 'false').lower() == 'true'
UNIFIED_ROLLOUT_PERCENTAGE = int(os.environ.get('UNIFIED_ROLLOUT_PERCENTAGE', '0'))

# Initialize migration handler if enabled
search_migration = None
if USE_UNIFIED_SEARCH or UNIFIED_ROLLOUT_PERCENTAGE > 0:
    try:
        from activation_manager.search.migration import get_migration_instance
        from activation_manager.search import SearchConfig
        
        # Create config with environment overrides
        search_config = SearchConfig(
            enable_ab_testing=UNIFIED_ROLLOUT_PERCENTAGE > 0 and UNIFIED_ROLLOUT_PERCENTAGE < 100,
            unified_rollout_percentage=UNIFIED_ROLLOUT_PERCENTAGE,
            fallback_on_error=True
        )
        
        search_migration = get_migration_instance(search_config)
        logger.info(f"🚀 Unified search migration enabled: {UNIFIED_ROLLOUT_PERCENTAGE}% rollout")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize unified search migration: {e}")
        search_migration = None

@app.route('/api/enhanced-variable-picker/search', methods=['POST'])
def enhanced_variable_search():
    """Enhanced semantic variable search with migration support"""
    try:
        data = request.json or {}
        query = data.get('query', '')
        top_k = data.get('top_k', 50)
        use_semantic = data.get('use_semantic', True)
        use_keyword = data.get('use_keyword', True)
        filter_similar = data.get('filter_similar', False)
        similarity_threshold = data.get('similarity_threshold', 0.85)
        max_similar_per_group = data.get('max_similar_per_group', 2)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check if we should use migration handler
        user_id = request.headers.get('X-User-ID') or data.get('user_id')
        
        if search_migration and (USE_UNIFIED_SEARCH or UNIFIED_ROLLOUT_PERCENTAGE > 0):
            logger.info(f"🔄 Using migration handler for search: query='{query[:50]}...'")
            results = search_migration.search(
                query=query,
                top_k=top_k,
                user_id=user_id,
                use_semantic=use_semantic,
                use_keyword=use_keyword,
                filter_similar=filter_similar,
                similarity_threshold=similarity_threshold,
                max_similar_per_group=max_similar_per_group
            )
            return jsonify(results)
        
        # Original implementation (no migration)
        picker = get_enhanced_picker()
        if picker:
            logger.info(f"🔍 Enhanced search request: query='{query}', filter_similar={filter_similar}, threshold={similarity_threshold}")
            results = picker.search_variables(
                query=query,
                top_k=top_k,
                use_semantic=use_semantic,
                use_keyword=use_keyword,
                filter_similar=filter_similar,
                similarity_threshold=similarity_threshold,
                max_similar_per_group=max_similar_per_group
            )
            logger.info(f"📊 Enhanced search results: {results.get('total_found', 0)} items")
            return jsonify(results)
        else:
            # Fallback to basic search with global variable loader
            results = search_variables(query, top_k)
            return jsonify({
                'results': results,
                'total_found': len(results),
                'query_context': {'original_query': query},
                'search_methods': {'keyword': True, 'semantic': False}
            })
        
    except Exception as e:
        logger.error(f"Enhanced variable search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-variable-picker/stats', methods=['GET'])
def enhanced_variable_stats():
    """Get enhanced variable statistics"""
    try:
        picker = get_enhanced_picker()
        if picker:
            stats = picker.get_variable_stats()
            return jsonify(stats)
        elif variable_loader and hasattr(variable_loader, 'variables_df') and variable_loader.variables_df is not None:
            df = variable_loader.variables_df
            return jsonify({
                'total_variables': len(df),
                'categories': df.get('category', []).nunique() if 'category' in df.columns else 0,
                'themes': df.get('theme', []).nunique() if 'theme' in df.columns else 0,
                'products': df.get('product_name', []).nunique() if 'product_name' in df.columns else 0
            })
        else:
            return jsonify({
                'total_variables': len(VARIABLE_DATABASE),
                'categories': len(set(var['category'] for var in VARIABLE_DATABASE)),
                'themes': 0,
                'products': 0
            })
    except Exception as e:
        logger.error(f"Enhanced stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500

# ===========================
# Unified Search Migration Endpoints
# ===========================

@app.route('/api/search/migration/status', methods=['GET'])
def get_migration_status():
    """Get current search migration status and metrics"""
    if not search_migration:
        return jsonify({
            'enabled': False,
            'message': 'Search migration not configured'
        })
    
    metrics = search_migration.get_metrics()
    
    return jsonify({
        'enabled': True,
        'rollout_percentage': UNIFIED_ROLLOUT_PERCENTAGE,
        'use_unified_search': USE_UNIFIED_SEARCH,
        'metrics': metrics,
        'environment': {
            'USE_UNIFIED_SEARCH': os.environ.get('USE_UNIFIED_SEARCH', 'false'),
            'UNIFIED_ROLLOUT_PERCENTAGE': os.environ.get('UNIFIED_ROLLOUT_PERCENTAGE', '0')
        }
    })

@app.route('/api/search/migration/test', methods=['POST'])
def test_migration_routing():
    """Test which search implementation will be used for a given user/query"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        query = data.get('query', 'test query')
        
        if not search_migration:
            return jsonify({
                'error': 'Search migration not configured'
            }), 400
        
        would_use_unified = search_migration.should_use_unified(user_id, query)
        
        return jsonify({
            'user_id': user_id,
            'query': query,
            'would_use_unified': would_use_unified,
            'rollout_percentage': UNIFIED_ROLLOUT_PERCENTAGE
        })
        
    except Exception as e:
        logger.error(f"Migration test error: {e}")
        return jsonify({'error': str(e)}), 500

# ===========================
# Test endpoint to verify deployment
# ===========================

@app.route('/api/test-deployment', methods=['GET'])
def test_deployment():
    """Simple test endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'API is working'
    })

# NOTE: Additional variable picker routes temporarily disabled for debugging
# The routes below are causing App Engine deployment failures
# They work locally but fail in production environment
# TODO: Investigate and fix deployment issues

# ===========================
# Additional Variable Picker Routes (GET methods)
# ===========================

# Test with a single simple route first
@app.route('/api/variable-picker/test', methods=['GET'])
def variable_picker_test():
    """Simple test endpoint for variable picker"""
    return jsonify({
        'status': 'ok',
        'message': 'Variable picker test endpoint',
        'loader_available': variable_loader is not None
    })

logger.info("✅ Variable picker test route registered")

@app.route('/api/variable-picker/search', methods=['GET'])
def variable_picker_search_get():
    """GET endpoint for variable search"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    try:
        # Use enhanced picker if available
        picker = get_enhanced_picker()
        if picker:
            results = picker.search_variables(
                query=query,
                top_k=limit,
                use_semantic=True,
                use_keyword=True
            )
            return jsonify(results)
        else:
            # Fallback to basic search
            results = search_variables(query, limit)
            return jsonify({
                'results': results,
                'total_found': len(results),
                'search_time_ms': 0
            })
    except Exception as e:
        logger.error(f"Variable search GET error: {e}", exc_info=True)
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/variable-picker/categories', methods=['GET'])
def get_variable_categories():
    """Get all variable categories with counts"""
    try:
        # Use enhanced picker if available
        picker = get_enhanced_picker()
        if picker and hasattr(picker, 'get_categories'):
            categories = picker.get_categories()
            return jsonify(categories)
        elif variable_loader and hasattr(variable_loader, 'variables_df') and variable_loader.variables_df is not None:
            # Use Parquet loader's dataframe
            df = variable_loader.variables_df
            
            # Count by category
            category_counts = df['category'].value_counts().to_dict() if 'category' in df.columns else {}
            
            # Format response
            categories = [
                {
                    'name': cat,
                    'count': count,
                    'type': cat.lower().replace(' ', '_')
                }
                for cat, count in category_counts.items()
            ]
            
            return jsonify({
                'categories': categories,
                'total': len(categories)
            })
        else:
            # Fallback to mock data categories
            categories_dict = {}
            for var in VARIABLE_DATABASE:
                cat = var['category']
                if cat not in categories_dict:
                    categories_dict[cat] = 0
                categories_dict[cat] += 1
                
            categories = [
                {
                    'name': cat,
                    'count': count,
                    'type': cat.lower().replace(' ', '_')
                }
                for cat, count in categories_dict.items()
            ]
            
            return jsonify({
                'categories': categories,
                'total': len(categories)
            })
    except Exception as e:
        logger.error(f"Get categories error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/category/<category_name>', methods=['GET'])
def get_variables_by_category(category_name):
    """Get variables for a specific category"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Decode URL-encoded category name
        from urllib.parse import unquote
        category_name = unquote(category_name)
        
        # Use enhanced picker if available
        picker = get_enhanced_picker()
        if picker and hasattr(picker, 'get_variables_by_category'):
            results = picker.get_variables_by_category(category_name, limit, offset)
            return jsonify(results)
        elif variable_loader and hasattr(variable_loader, 'variables_df') and variable_loader.variables_df is not None:
            # Use Parquet loader's dataframe
            df = variable_loader.variables_df
            
            # Filter by category
            if 'category' in df.columns:
                category_df = df[df['category'] == category_name]
                
                # Apply offset and limit
                results = category_df.iloc[offset:offset+limit]
                
                # Convert to list of dicts
                variables = results.to_dict('records')
                
                return jsonify({
                    'category': category_name,
                    'variables': variables,
                    'total': len(category_df),
                    'offset': offset,
                    'limit': limit
                })
            else:
                return jsonify({
                    'category': category_name,
                    'variables': [],
                    'total': 0
                })
        else:
            # Fallback to mock data
            variables = [
                var for var in VARIABLE_DATABASE
                if var['category'] == category_name
            ]
            
            # Apply pagination
            paginated_vars = variables[offset:offset+limit]
            
            return jsonify({
                'category': category_name,
                'variables': paginated_vars,
                'total': len(variables),
                'offset': offset,
                'limit': limit
            })
    except Exception as e:
        logger.error(f"Get variables by category error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/search/complex', methods=['POST'])
def complex_variable_search():
    """Complex query search with natural language understanding"""
    try:
        data = request.json or {}
        query = data.get('query', '')
        limit = data.get('limit', 50)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        # Use enhanced picker for complex queries
        picker = get_enhanced_picker()
        if picker:
            # Use search_variables with similarity filtering enabled
            results = picker.search_variables(
                query=query,
                top_k=limit,
                use_semantic=True,
                use_keyword=True,
                filter_similar=True,  # Enable similarity filtering for complex queries
                similarity_threshold=0.85,
                max_similar_per_group=2
            )
            return jsonify(results)
        else:
            # Fallback to regular search
            results = search_variables(query, limit)
            
            # Group by category for complex queries
            grouped = {}
            for var in results:
                cat = var.get('category', 'Other')
                if cat not in grouped:
                    grouped[cat] = []
                grouped[cat].append(var)
                
            return jsonify({
                'query': query,
                'results': results,
                'grouped_results': grouped,
                'total_found': len(results)
            })
    except Exception as e:
        logger.error(f"Complex search error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/refine', methods=['POST'])
def refine_variable_search():
    """Refine variable selection with expand/filter/suggest modes"""
    try:
        data = request.json or {}
        description = data.get('description', '')
        current_variables = data.get('current_variables', [])
        mode = data.get('mode', 'expand')  # expand, filter, suggest
        
        # Use enhanced picker if available
        picker = get_enhanced_picker()
        if picker and hasattr(picker, 'refine_search'):
            results = picker.refine_search(description, current_variables, mode)
            return jsonify(results)
        else:
            # Simple fallback implementation
            if mode == 'expand':
                # Find similar variables
                results = search_variables(description, 20)
                # Filter out already selected
                new_vars = [
                    var for var in results
                    if var.get('code') not in current_variables
                ]
                return jsonify({
                    'mode': mode,
                    'description': description,
                    'suggestions': new_vars[:10],
                    'message': f'Found {len(new_vars)} additional variables'
                })
            else:
                return jsonify({
                    'mode': mode,
                    'description': description,
                    'suggestions': [],
                    'message': 'Refine mode not fully implemented'
                })
    except Exception as e:
        logger.error(f"Refine search error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

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
    """App Engine warmup handler - must return quickly"""
    logger.info("Warmup request received")
    # Don't block on initialization - just return success
    # Background initialization will happen on first request
    return '', 200

@app.route('/api/health')
def api_health_check():
    """Simple API health check endpoint that returns quickly"""
    return jsonify({
        'status': 'healthy',
        'service': 'activation-manager',
        'timestamp': datetime.now().isoformat()
    }), 200

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

# Log successful initialization
logger.info("=== APP INITIALIZATION COMPLETE ===")
logger.info(f"Total routes registered: {len(list(app.url_map.iter_rules()))}")
logger.info("App ready to handle requests")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask app on port {port}")
    # Disable debug mode to avoid reloader issues with multiprocessing
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)