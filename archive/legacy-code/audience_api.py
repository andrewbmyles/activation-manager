"""
Flask API for Audience Builder
Provides REST endpoints for variable selection, data retrieval, and clustering
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from audience_builder import AudienceBuilder
from variable_catalog import get_full_catalog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize with environment variables
DATA_PATH = os.getenv('DATA_PATH', "/Users/myles/Documents/Activation Manager/Synthetic_Data/output/synthetic_consumer_data_1000_20250525_155201.csv")
SAMPLE_SIZE = int(os.getenv('SAMPLE_SIZE', '100'))  # Default to 100 for development

builder = AudienceBuilder(
    variable_catalog=get_full_catalog(),
    data_path=DATA_PATH
)

# Load data once at startup
builder.data_retriever.load_data()
print(f"Data loaded: {builder.data_retriever.data.shape[0]} rows")
print(f"Using sample size: {SAMPLE_SIZE} for cost-efficient development")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Audience Builder API',
        'data_loaded': builder.data_retriever.data is not None
    })


@app.route('/api/variable_selector', methods=['POST'])
def variable_selector():
    """
    Analyze user request and suggest relevant variables
    
    Expected JSON body:
    {
        "user_request": "I need to find environmentally conscious millennials..."
    }
    """
    try:
        data = request.json
        user_request = data.get('user_request', '')
        
        if not user_request:
            return jsonify({
                'error': 'user_request is required',
                'status': 'error'
            }), 400
        
        # Use the variable selector
        suggestions = builder.variable_selector.analyze_request(user_request)
        
        return jsonify({
            'suggestions': suggestions[:10],
            'total_found': len(suggestions),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/data_retriever', methods=['POST'])
def data_retriever():
    """
    Fetch data for selected variables
    
    Expected JSON body:
    {
        "variable_codes": ["Q470010C01", "Q470030C01", ...],
        "sample_size": 1000  # optional
    }
    """
    try:
        data = request.json
        variable_codes = data.get('variable_codes', [])
        sample_size = data.get('sample_size', None)
        
        if not variable_codes:
            return jsonify({
                'error': 'variable_codes list is required',
                'status': 'error'
            }), 400
        
        # Fetch data - use configured sample size if not specified
        if sample_size is None:
            sample_size = SAMPLE_SIZE
        df = builder.data_retriever.fetch_data(variable_codes, sample_size)
        
        # Convert to JSON-serializable format
        return jsonify({
            'data': df.to_dict('records')[:100],  # Return first 100 rows for preview
            'shape': list(df.shape),
            'columns': list(df.columns),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/cluster_analyzer', methods=['POST'])
def cluster_analyzer():
    """
    Perform clustering on provided data
    
    Expected JSON body:
    {
        "variable_codes": ["Q470010C01", "Q470030C01", ...],
        "sample_size": 1000  # optional
    }
    """
    try:
        data = request.json
        variable_codes = data.get('variable_codes', [])
        sample_size = data.get('sample_size', None)
        
        if not variable_codes:
            return jsonify({
                'error': 'variable_codes list is required',
                'status': 'error'
            }), 400
        
        # Build audience with clustering
        results = builder.build_audience("", variable_codes)
        
        # Get group profiles
        profiles = builder.get_group_profiles()
        
        # Prepare summary statistics
        group_summary = []
        for group_id, profile in profiles.items():
            summary = {
                'group_id': group_id,
                'size': profile['size'],
                'percentage': profile['percentage'],
                'key_characteristics': []
            }
            
            # Extract top 3 most distinctive characteristics
            for var_code, stats in profile['characteristics'].items():
                if 'dominant_value' in stats:
                    summary['key_characteristics'].append({
                        'variable': var_code,
                        'value': stats['dominant_value'],
                        'strength': stats['percentage']
                    })
                elif 'mean' in stats:
                    summary['key_characteristics'].append({
                        'variable': var_code,
                        'mean': stats['mean'],
                        'median': stats['median']
                    })
            
            # Limit to top 5 characteristics
            summary['key_characteristics'] = summary['key_characteristics'][:5]
            group_summary.append(summary)
        
        return jsonify({
            'groups': group_summary,
            'total_records': len(results),
            'num_groups': len(profiles),
            'profiles': profiles,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/variables', methods=['GET'])
def list_variables():
    """List all available variables"""
    try:
        catalog = get_full_catalog()
        
        # Group variables by type
        grouped = {}
        for code, info in catalog.items():
            var_type = info.get('type', 'other')
            if var_type not in grouped:
                grouped[var_type] = []
            grouped[var_type].append({
                'code': code,
                'description': info.get('description', ''),
                'data_type': info.get('data_type', 'numeric')
            })
        
        return jsonify({
            'variables': grouped,
            'total_count': len(catalog),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_audience():
    """
    Complete audience analysis endpoint
    Combines variable selection and clustering in one call
    
    Expected JSON body:
    {
        "user_request": "I need to find environmentally conscious millennials...",
        "auto_select": true,  # optional, auto-select top variables
        "sample_size": 1000   # optional
    }
    """
    try:
        data = request.json
        user_request = data.get('user_request', '')
        auto_select = data.get('auto_select', False)
        sample_size = data.get('sample_size', None)
        
        if not user_request:
            return jsonify({
                'error': 'user_request is required',
                'status': 'error'
            }), 400
        
        # Step 1: Analyze request and get variable suggestions
        suggestions = builder.variable_selector.analyze_request(user_request)
        
        if not suggestions:
            return jsonify({
                'error': 'No relevant variables found for your request',
                'suggestions': [],
                'status': 'error'
            }), 404
        
        # Step 2: Auto-select top variables if requested
        if auto_select:
            # Select top 5-8 variables with highest scores
            selected_codes = [var['code'] for var in suggestions[:7]]
            
            # Step 3: Build audience with clustering
            results = builder.build_audience(user_request, selected_codes)
            profiles = builder.get_group_profiles()
            
            # Prepare response
            return jsonify({
                'request': user_request,
                'selected_variables': selected_codes,
                'groups': len(profiles),
                'profiles': profiles,
                'suggestions': suggestions[:10],
                'status': 'success'
            })
        else:
            # Return suggestions for user to confirm
            return jsonify({
                'request': user_request,
                'suggestions': suggestions[:10],
                'auto_select': False,
                'status': 'success',
                'message': 'Please confirm variable selection'
            })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Chat endpoint for Claude integration
    Processes natural language requests through Claude
    """
    try:
        data = request.json
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({
                'error': 'message is required',
                'status': 'error'
            }), 400
        
        # For now, directly process as an audience request
        # In production, this would go through Claude for more sophisticated handling
        
        # Analyze the message as an audience request
        suggestions = builder.variable_selector.analyze_request(message)
        
        if suggestions:
            # Auto-select top variables
            selected_codes = [var['code'] for var in suggestions[:7]]
            
            # Build audience
            results = builder.build_audience(message, selected_codes)
            profiles = builder.get_group_profiles()
            
            # Format response
            response_message = f"I've created {len(profiles)} audience segments based on your request.\n\n"
            
            for group_id, profile in profiles.items():
                response_message += f"**Segment {int(group_id) + 1}** ({profile['percentage']}% - {profile['size']} records)\n"
                response_message += "Key characteristics:\n"
                
                char_count = 0
                for var_code, stats in profile.get('characteristics', {}).items():
                    if char_count >= 3:
                        break
                    if 'dominant_value' in stats:
                        response_message += f"- {var_code}: {stats['dominant_value']} ({stats['percentage']:.1f}%)\n"
                    elif 'mean' in stats:
                        response_message += f"- {var_code}: Average {stats['mean']:.1f}\n"
                    char_count += 1
                response_message += "\n"
            
            return jsonify({
                'message': response_message,
                'api_response': {
                    'profiles': profiles,
                    'selected_variables': selected_codes,
                    'status': 'success'
                },
                'status': 'success'
            })
        else:
            return jsonify({
                'message': 'No relevant variables found for your request. Please try describing your audience differently.',
                'status': 'warning'
            })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


if __name__ == '__main__':
    print("Starting Audience Builder API...")
    print(f"Data path: {DATA_PATH}")
    print("API endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/variables")
    print("  - POST /api/variable_selector")
    print("  - POST /api/data_retriever")
    print("  - POST /api/cluster_analyzer")
    print("  - POST /api/analyze")
    print("  - POST /api/chat")
    app.run(debug=True, port=5000)