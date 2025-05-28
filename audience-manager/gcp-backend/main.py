import os
import json
import random
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with specific origins
ALLOWED_ORIGINS = [
    "https://audience-manager.vercel.app",
    "https://audience-manager-*.vercel.app",  # Allow preview deployments
    "http://localhost:3000",  # Local development
]

# Initialize CORS with proper configuration
CORS(app, 
     origins=ALLOWED_ORIGINS,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# In-memory storage (replace with real database in production)
sessions = {}
audiences = []
segments = []

# Authentication decorator (optional - for protected endpoints)
def auth_optional(f):
    """Decorator that makes authentication optional"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Validate token if provided
            try:
                # In production, verify the Google ID token here
                # For now, we'll just log it
                logger.info(f"Auth header present: {auth_header[:20]}...")
            except Exception as e:
                logger.error(f"Auth validation error: {e}")
        return f(*args, **kwargs)
    return decorated_function

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        "status": "healthy",
        "service": "audience-manager-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

# API Info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Audience Manager API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "start_session": "/api/nl/start_session",
            "process": "/api/nl/process",
            "audiences": "/api/audiences",
            "export": "/api/export/<audience_id>"
        }
    })

# Natural Language API endpoints
@app.route('/api/nl/start_session', methods=['POST', 'OPTIONS'])
@auth_optional
def start_session():
    """Start a new NL processing session"""
    if request.method == 'OPTIONS':
        return '', 204
    
    session_id = f"session_{random.randint(1000, 9999)}"
    sessions[session_id] = {
        "created": datetime.now().isoformat(),
        "status": "active"
    }
    
    logger.info(f"Created session: {session_id}")
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST', 'OPTIONS'])
@auth_optional
def process_workflow():
    """Process NL workflow actions"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        action = data.get('action')
        session_id = data.get('session_id')
        
        logger.info(f"Processing action: {action} for session: {session_id}")
        
        if action == 'process':
            # Simulate variable suggestion
            return jsonify({
                "status": "variables_suggested",
                "suggested_variables": {
                    "demographic": [
                        {
                            "code": "age_range",
                            "description": "Age Range",
                            "type": "demographic",
                            "relevance_score": 0.9,
                            "category": "Demographics"
                        },
                        {
                            "code": "income_level",
                            "description": "Household Income Level",
                            "type": "demographic",
                            "relevance_score": 0.85,
                            "category": "Demographics"
                        },
                        {
                            "code": "location",
                            "description": "Geographic Location",
                            "type": "demographic",
                            "relevance_score": 0.8,
                            "category": "Geography"
                        }
                    ],
                    "behavioral": [
                        {
                            "code": "purchase_frequency",
                            "description": "Purchase Frequency",
                            "type": "behavioral",
                            "relevance_score": 0.75,
                            "category": "Behavioral"
                        },
                        {
                            "code": "engagement_level",
                            "description": "Engagement Level",
                            "type": "behavioral",
                            "relevance_score": 0.7,
                            "category": "Behavioral"
                        }
                    ]
                }
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
                    "dominantTraits": ["High Value", "Engaged", "Urban"],
                    "prizm_profile": {
                        "dominant_segments": [f"PRIZM_{i+1}"],
                        "demographics": "Mixed demographics",
                        "key_behaviors": ["Digital Native", "Brand Conscious"]
                    }
                })
            
            audience_id = f"aud_{random.randint(1000, 9999)}"
            
            # Store audience
            audiences.append({
                "id": audience_id,
                "segments": segments,
                "created": datetime.now().isoformat()
            })
            
            return jsonify({
                "status": "complete",
                "segments": segments,
                "audience_id": audience_id
            })
        
        else:
            return jsonify({
                "status": "error",
                "message": f"Unknown action: {action}"
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing workflow: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/audiences', methods=['GET', 'POST', 'OPTIONS'])
@auth_optional
def handle_audiences():
    """Handle audience CRUD operations"""
    if request.method == 'OPTIONS':
        return '', 204
    
    if request.method == 'GET':
        return jsonify(audiences)
    
    elif request.method == 'POST':
        try:
            audience = request.json
            audience['id'] = f"aud_{random.randint(1000, 9999)}"
            audience['createdAt'] = datetime.now().isoformat()
            audience['updatedAt'] = datetime.now().isoformat()
            audiences.append(audience)
            
            logger.info(f"Created audience: {audience['id']}")
            return jsonify(audience), 201
            
        except Exception as e:
            logger.error(f"Error creating audience: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/export/<audience_id>', methods=['GET', 'OPTIONS'])
@auth_optional
def export_audience(audience_id):
    """Export audience data as CSV"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Find audience
        audience = next((a for a in audiences if a['id'] == audience_id), None)
        
        if not audience:
            return jsonify({"error": "Audience not found"}), 404
        
        # Generate CSV
        csv_content = "segment_id,segment_name,size,percentage\n"
        
        if 'segments' in audience:
            for segment in audience['segments']:
                csv_content += f"{segment['group_id']},{segment.get('name', 'Segment ' + str(segment['group_id']))},{segment['size']},{segment['size_percentage']:.2f}\n"
        else:
            # Generate sample data if no segments
            for i in range(4):
                csv_content += f"{i},Segment_{i},{random.randint(1000, 5000)},{random.uniform(5, 10):.2f}\n"
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=audience_{audience_id}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting audience: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Audience Manager API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)