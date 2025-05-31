import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])

# In-memory storage for demo
sessions = {}
audiences = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    session_id = f"session_{random.randint(1000, 9999)}"
    sessions[session_id] = {"created": datetime.now().isoformat()}
    return jsonify({"session_id": session_id})

@app.route('/api/nl/process', methods=['POST'])
def process():
    data = request.json
    action = data.get('action')
    
    if action == 'process':
        return jsonify({
            "status": "variables_suggested",
            "suggested_variables": {
                "demographic": [
                    {"code": "age", "description": "Age Range", "type": "demographic", "relevance_score": 0.9},
                    {"code": "income", "description": "Income Level", "type": "demographic", "relevance_score": 0.85}
                ],
                "behavioral": [
                    {"code": "purchase", "description": "Purchase Behavior", "type": "behavioral", "relevance_score": 0.8}
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
                "name": f"Segment {i+1}"
            })
        return jsonify({
            "status": "complete",
            "segments": segments,
            "audience_id": f"aud_{random.randint(1000, 9999)}"
        })
    
    return jsonify({"status": "error", "message": "Unknown action"})

@app.route('/api/export/<audience_id>', methods=['GET'])
def export(audience_id):
    csv_data = "id,segment,size\n"
    for i in range(4):
        csv_data += f"{i},segment_{i},{random.randint(1000, 5000)}\n"
    
    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=audience_{audience_id}.csv'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
