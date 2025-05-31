import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Sample data storage (in production, use a real database)
audiences = []
segments = []

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "audience-manager-api"})

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    session_id = f"session_{random.randint(1000, 9999)}"
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST'])
def process_workflow():
    data = request.json
    action = data.get('action')
    
    if action == 'process':
        # Simulate variable suggestion
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

@app.route('/api/audiences', methods=['GET', 'POST'])
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
def export_audience(audience_id):
    # Simulate CSV export
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
