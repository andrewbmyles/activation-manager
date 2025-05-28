import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import secrets
import json
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True, origins=['https://tobermory.ai', 'http://localhost:3000', 'https://audience-manager-593977832320.us-central1.run.app'])

# Simple user storage (in production, use a database)
USERS = {
    'andrew@tobermory.ai': generate_password_hash('admin')
}

# Sample data storage
audiences = []
segments = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return jsonify({
        "message": "Audience Manager API",
        "version": "1.0.0",
        "authenticated": 'user' in session
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
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
        return jsonify({
            "status": "variables_suggested",
            "suggested_variables": {
                "demographic": [
                    {"code": "age", "description": "Age Range", "type": "demographic", "relevance_score": 0.9},
                    {"code": "income", "description": "Income Level", "type": "demographic", "relevance_score": 0.85},
                    {"code": "location", "description": "Geographic Location", "type": "demographic", "relevance_score": 0.8}
                ],
                "behavioral": [
                    {"code": "purchase_freq", "description": "Purchase Frequency", "type": "behavioral", "relevance_score": 0.75},
                    {"code": "engagement", "description": "Engagement Level", "type": "behavioral", "relevance_score": 0.7}
                ]
            }
        })
    elif action == 'confirm':
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

@app.route('/api/audiences', methods=['GET', 'POST'])
@login_required
def handle_audiences():
    if request.method == 'GET':
        return jsonify(audiences)
    elif request.method == 'POST':
        audience = request.json
        audience['id'] = f"aud_{random.randint(1000, 9999)}"
        audience['createdAt'] = datetime.now().isoformat()
        audiences.append(audience)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)