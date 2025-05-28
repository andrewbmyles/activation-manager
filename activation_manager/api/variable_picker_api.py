"""
Variable Picker API - RESTful endpoints for the variable picker tool
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import logging
from typing import Dict, Any

from ..core.variable_picker_tool import VariablePickerTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize variable picker tool
openai_key = os.environ.get('OPENAI_API_KEY', '')
variable_picker = VariablePickerTool(use_embeddings=True, openai_api_key=openai_key)

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
    """
    Start a new variable picker session
    
    Expected JSON body:
    {
        "query": "natural language query"
    }
    """
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
        logger.error(f"Error starting session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/refine/<session_id>', methods=['POST'])
def refine_search(session_id: str):
    """
    Refine search for a session
    
    Expected JSON body:
    {
        "refinement": "additional criteria",
        "exclude_codes": ["VAR1", "VAR2"]  // optional
    }
    """
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
        logger.error(f"Error refining search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/confirm/<session_id>', methods=['POST'])
def confirm_variables(session_id: str):
    """
    Confirm selected variables
    
    Expected JSON body:
    {
        "confirmed_codes": ["VAR1", "VAR2", "VAR3"]
    }
    """
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
        logger.error(f"Error confirming variables: {e}")
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
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/cancel/<session_id>', methods=['POST'])
def cancel_session(session_id: str):
    """Cancel a session"""
    try:
        response = variable_picker.cancel_session(session_id)
        
        if 'error' in response:
            return jsonify(response), 404
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error cancelling session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/variable-picker/export/<session_id>', methods=['GET'])
def export_variables(session_id: str):
    """
    Export confirmed variables
    
    Query parameters:
    - format: json (default), csv, list
    """
    try:
        format_type = request.args.get('format', 'json')
        
        result = variable_picker.export_confirmed_variables(session_id, format=format_type)
        
        if format_type == 'csv':
            # Return as CSV download
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
        logger.error(f"Error exporting variables: {e}")
        return jsonify({'error': str(e)}), 500

# Workflow endpoint for complete variable selection
@app.route('/api/variable-picker/workflow', methods=['POST'])
def variable_selection_workflow():
    """
    Complete variable selection workflow in one endpoint
    
    Expected JSON body:
    {
        "query": "natural language query",
        "auto_confirm_top": 5  // optional, auto-confirm top N results
    }
    
    Returns the top variables for the query
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        # Create temporary session
        session_id = str(uuid.uuid4())
        
        # Start session and process query
        variable_picker.start_session(session_id, data['query'])
        response = variable_picker.process_nl_query(session_id, data['query'])
        
        # Auto-confirm if requested
        if 'auto_confirm_top' in data:
            top_n = min(data['auto_confirm_top'], len(response['variables']))
            confirmed_codes = [var['code'] for var in response['variables'][:top_n]]
            
            confirm_response = variable_picker.confirm_variables(session_id, confirmed_codes)
            response.update(confirm_response)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the API server
    port = int(os.environ.get('VARIABLE_PICKER_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)