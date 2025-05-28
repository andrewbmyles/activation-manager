"""
Standalone Variable Picker API Server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.variable_picker_tool import VariablePickerTool

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

# Initialize variable picker with your API key
api_key = os.environ.get('OPENAI_API_KEY', '')
variable_picker = VariablePickerTool(use_embeddings=True, openai_api_key=api_key)

@app.route('/api/variable-picker/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'variable-picker',
        'embeddings_enabled': variable_picker.use_embeddings
    })

@app.route('/api/variable-picker/start', methods=['POST'])
def start_session():
    """Start a new variable picker session"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Start session
        session = variable_picker.start_session(session_id, data['query'])
        
        # Process initial query
        response = variable_picker.process_nl_query(
            session_id, 
            data['query'],
            top_k=data.get('top_k', 20)
        )
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error starting session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST'])
def refine_search(session_id: str):
    """Refine search for a session"""
    try:
        data = request.get_json()
        
        if not data or 'refinement' not in data:
            return jsonify({'error': 'Missing refinement parameter'}), 400
        
        response = variable_picker.refine_search(
            session_id,
            data['refinement'],
            exclude_codes=data.get('exclude_codes')
        )
        
        return jsonify(response)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error refining search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST'])
def confirm_variables(session_id: str):
    """Confirm selected variables"""
    try:
        data = request.get_json()
        
        if not data or 'confirmed_codes' not in data:
            return jsonify({'error': 'Missing confirmed_codes parameter'}), 400
        
        response = variable_picker.confirm_variables(
            session_id,
            data['confirmed_codes']
        )
        
        return jsonify(response)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error confirming variables: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/status/<session_id>', methods=['GET'])
def get_status(session_id: str):
    """Get session status"""
    try:
        response = variable_picker.get_session_status(session_id)
        
        if 'error' in response:
            return jsonify(response), 404
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/export/<session_id>', methods=['GET'])
def export_variables(session_id: str):
    """Export confirmed variables"""
    try:
        format_type = request.args.get('format', 'json')
        
        result = variable_picker.export_confirmed_variables(session_id, format=format_type)
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if result:
                writer = csv.DictWriter(output, fieldnames=result[0].keys())
                writer.writeheader()
                writer.writerows(result)
            
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=variables_{session_id}.csv'
            }
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error exporting variables: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Variable Picker API Server...")
    print("✅ Loaded full dataset with embeddings support")
    print(f"🚀 Server running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)