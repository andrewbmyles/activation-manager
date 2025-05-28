import os
import json
import h5py
import numpy as np
import faiss
import openai
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import secrets
from datetime import datetime
import random
from google.cloud import storage
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True, origins=['https://tobermory.ai', 'http://localhost:3000', 'https://audience-manager-593977832320.us-central1.run.app'])

# OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Simple user storage (in production, use database)
USERS = {
    'andrew@tobermory.ai': generate_password_hash('admin')
}

# Global embedding searcher (initialized once)
embedding_searcher = None

class EmbeddingSearcher:
    """Fast similarity search using pre-computed embeddings"""
    
    def __init__(self, bucket_name='audience-manager-embeddings'):
        self.bucket_name = bucket_name
        self.metadata = None
        self.index = None
        self.embeddings = None
        self.embedding_map = {}
        self._load_from_gcs()
    
    def _load_from_gcs(self):
        """Load embeddings and metadata from Google Cloud Storage"""
        try:
            logger.info("Loading embeddings from GCS...")
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            
            # Download files to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download metadata
                metadata_blob = bucket.blob('embeddings/metadata.json')
                metadata_path = os.path.join(temp_dir, 'metadata.json')
                metadata_blob.download_to_filename(metadata_path)
                
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                
                # Download embeddings
                embeddings_blob = bucket.blob('embeddings/embeddings.h5')
                embeddings_path = os.path.join(temp_dir, 'embeddings.h5')
                embeddings_blob.download_to_filename(embeddings_path)
                
                # Load embeddings into memory
                self._load_embeddings(embeddings_path)
                
            logger.info(f"Loaded {len(self.metadata)} variables with embeddings")
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            # Fallback to empty state
            self.metadata = []
            self.embeddings = np.array([])
            self.index = None
    
    def _load_embeddings(self, embeddings_path):
        """Load embeddings from H5 file and build FAISS index"""
        self.embeddings = []
        
        with h5py.File(embeddings_path, 'r') as f:
            for idx, item in enumerate(self.metadata):
                code = item['code']
                if f'embeddings/{code}' in f:
                    emb = f[f'embeddings/{code}'][:]
                    
                    # Store average embedding for each variable
                    avg_embedding = np.mean(emb, axis=0)
                    self.embeddings.append(avg_embedding)
                    
                    self.embedding_map[code] = {
                        'index': idx,
                        'all_embeddings': emb
                    }
        
        self.embeddings = np.array(self.embeddings).astype('float32')
        
        # Build FAISS index
        if len(self.embeddings) > 0:
            faiss.normalize_L2(self.embeddings)
            self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
            self.index.add(self.embeddings)
            logger.info(f"Built FAISS index with {len(self.embeddings)} embeddings")
    
    def search(self, query, top_k=15):
        """Search for similar variables using embeddings"""
        if self.index is None or len(self.embeddings) == 0:
            logger.warning("No embeddings available, returning empty results")
            return []
        
        try:
            # Get query embedding from OpenAI
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = np.array(response['data'][0]['embedding']).astype('float32')
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.embeddings)))
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata):
                    metadata = self.metadata[idx]
                    results.append({
                        'code': metadata['code'],
                        'description': metadata['original_description'],
                        'category': metadata['category'],
                        'type': metadata.get('type', 'general'),
                        'source': metadata.get('source', 'unknown'),
                        'score': float(score) * 10,  # Scale to 0-10
                        'matched_descriptions': self._get_best_matches(
                            query_embedding[0], 
                            metadata['code']
                        )
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in embedding search: {e}")
            return []
    
    def _get_best_matches(self, query_emb, code, top_n=3):
        """Find which descriptions matched best"""
        try:
            if code not in self.embedding_map:
                return []
            
            all_emb = self.embedding_map[code]['all_embeddings']
            
            # Normalize embeddings
            all_emb_norm = all_emb / np.linalg.norm(all_emb, axis=1, keepdims=True)
            query_emb_norm = query_emb / np.linalg.norm(query_emb)
            
            similarities = np.dot(all_emb_norm, query_emb_norm)
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            metadata = self.metadata[self.embedding_map[code]['index']]
            all_descs = [metadata['original_description']] + metadata.get('generated_descriptions', [])
            
            matched = []
            for i in top_indices:
                if i < len(all_descs):
                    matched.append(all_descs[i])
            
            return matched
            
        except Exception as e:
            logger.error(f"Error getting best matches: {e}")
            return []

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize embedding searcher on startup
def initialize_embeddings():
    global embedding_searcher
    try:
        embedding_searcher = EmbeddingSearcher()
        logger.info("Embedding searcher initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedding searcher: {e}")
        embedding_searcher = None

# Routes
@app.route('/')
def index():
    return jsonify({
        "message": "Audience Manager API with Embeddings",
        "version": "2.0.0",
        "authenticated": 'user' in session,
        "embeddings_loaded": embedding_searcher is not None
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "embeddings_status": "loaded" if embedding_searcher else "not_loaded"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in USERS and check_password_hash(USERS[email], password):
        session['user'] = email
        return jsonify({
            'success': True,
            'user': email,
            'message': 'Login successful'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logout successful'})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user' in session:
        return jsonify({
            'authenticated': True,
            'user': session['user']
        })
    return jsonify({
        'authenticated': False
    })

@app.route('/api/nl/start_session', methods=['POST'])
@login_required
def start_session():
    session_id = f"session_{random.randint(1000, 9999)}"
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST'])
@login_required
def process_workflow():
    data = request.json
    action = data.get('action')
    
    if action == 'process':
        # Use embedding search for variable suggestions
        query = data.get('query', '')
        
        if embedding_searcher and query:
            # Use embedding-based search
            suggested_vars = embedding_searcher.search(query, top_k=15)
        else:
            # Fallback to default suggestions
            suggested_vars = [
                {"code": "age", "description": "Age Range", "type": "demographic", "score": 0.9},
                {"code": "income", "description": "Income Level", "type": "demographic", "score": 0.85},
                {"code": "location", "description": "Geographic Location", "type": "demographic", "score": 0.8}
            ]
        
        # Group by type
        grouped_vars = {}
        for var in suggested_vars:
            var_type = var.get('type', 'general')
            if var_type not in grouped_vars:
                grouped_vars[var_type] = []
            grouped_vars[var_type].append({
                "code": var['code'],
                "description": var['description'],
                "type": var_type,
                "relevance_score": var.get('score', 0.5)
            })
        
        return jsonify({
            "status": "variables_suggested",
            "suggested_variables": grouped_vars,
            "total_found": len(suggested_vars),
            "search_method": "embeddings" if embedding_searcher else "fallback"
        })
        
    elif action == 'confirm':
        # Simulate segment creation
        segments = []
        for i in range(4):
            segments.append({
                "group_id": i,
                "size": random.randint(10000, 50000),
                "size_percentage": random.uniform(5, 10),
                "name": f"Segment {i+1}",
                "dominantTraits": ["High Value", "Engaged", "Urban"]
            })
        
        return jsonify({
            "status": "complete",
            "segments": segments,
            "audience_id": f"aud_{random.randint(1000, 9999)}"
        })
    
    return jsonify({"status": "unknown_action"})

@app.route('/api/embeddings/search', methods=['POST'])
@login_required
def embedding_search():
    """Direct embedding search endpoint for testing"""
    data = request.get_json()
    query = data.get('query', '')
    top_k = data.get('top_k', 15)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    if not embedding_searcher:
        return jsonify({'error': 'Embeddings not loaded'}), 503
    
    results = embedding_searcher.search(query, top_k)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/api/embeddings/status', methods=['GET'])
@login_required
def embedding_status():
    """Check embedding service status"""
    if embedding_searcher:
        return jsonify({
            'status': 'loaded',
            'variable_count': len(embedding_searcher.metadata),
            'index_size': len(embedding_searcher.embeddings) if embedding_searcher.embeddings is not None else 0
        })
    else:
        return jsonify({
            'status': 'not_loaded',
            'variable_count': 0,
            'index_size': 0
        })

# Existing endpoints remain the same
@app.route('/api/audiences', methods=['GET', 'POST'])
@login_required
def handle_audiences():
    if request.method == 'GET':
        return jsonify([])  # Return empty list for now
    elif request.method == 'POST':
        audience = request.json
        audience['id'] = f"aud_{random.randint(1000, 9999)}"
        audience['createdAt'] = datetime.now().isoformat()
        return jsonify(audience), 201

@app.route('/api/export/<audience_id>', methods=['GET'])
@login_required
def export_audience(audience_id):
    csv_content = "id,segment,size\n"
    for i in range(4):
        csv_content += f"{i},{audience_id}_segment_{i},{random.randint(1000, 5000)}\n"
    
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=audience_{audience_id}.csv'
    }

# Initialize embeddings on startup
initialize_embeddings()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)