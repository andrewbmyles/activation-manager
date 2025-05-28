from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS
CORS(app, origins=["*"])

@app.route('/')
def home():
    return jsonify({"message": "Audience Manager API", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api')
def api_info():
    return jsonify({
        "name": "Audience Manager API",
        "version": "1.0.0",
        "endpoints": ["/health", "/api"]
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)