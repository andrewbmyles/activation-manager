# GCP-optimized version of the enhanced audience API
import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import redis
from functools import wraps
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced audience builder
from api.enhanced_nl_audience_builder import (
    EnhancedVariableSelector,
    DataRetriever,
    EnhancedAudienceBuilder
)

# Import GCP config
sys.path.append(os.path.join(os.path.dirname(__file__), '../../gcp'))
try:
    from config import gcp_config
    USE_GCP = True
except ImportError:
    USE_GCP = False
    print("Running without GCP config")

app = Flask(__name__)
CORS(app, origins=['https://*.vercel.app', 'http://localhost:3000'])

# Initialize Redis connection
redis_client = None
if USE_GCP:
    try:
        redis_url = gcp_config.get_redis_url()
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print(f"Connected to Redis")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None

# Initialize components
variable_selector = EnhancedVariableSelector()
data_retriever = DataRetriever('', '')
audience_builder = EnhancedAudienceBuilder(
    variable_catalog=variable_selector.get_catalog(),
    api_endpoint='',
    api_key=''
)

# Cache decorator
def cache_result(expiration=3600):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)
            
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                print(f"Cache read error: {e}")
            
            # Call function and cache result
            result = f(*args, **kwargs)
            
            try:
                redis_client.setex(
                    cache_key,
                    expiration,
                    json.dumps(result)
                )
            except Exception as e:
                print(f"Cache write error: {e}")
            
            return result
        return decorated_function
    return decorator

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for App Engine"""
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'redis': 'connected' if redis_client else 'disconnected',
        'gcp': 'enabled' if USE_GCP else 'disabled'
    }
    
    # Check Redis
    if redis_client:
        try:
            redis_client.ping()
        except:
            health_status['redis'] = 'error'
            health_status['status'] = 'degraded'
    
    return jsonify(health_status)

@app.route('/api/audience/process', methods=['POST'])
@cache_result(expiration=1800)  # Cache for 30 minutes
def process_audience():
    """Main endpoint for audience processing"""
    try:
        data = request.json
        action = data.get('action')
        payload = data.get('payload', {})
        
        print(f"Processing action: {action}")
        
        if action == 'search':
            # Natural language search
            query = payload.get('query', '')
            suggestions = variable_selector.semantic_search(query)
            
            return jsonify({
                'status': 'success',
                'suggestions': suggestions[:10],
                'query': query
            })
            
        elif action == 'confirm':
            # Handle variable confirmation and clustering
            confirmed_codes = payload.get('confirmed_variables', [])
            
            if not confirmed_codes:
                return jsonify({'error': 'No variables to confirm'}), 400
            
            print(f"Confirming variables: {confirmed_codes}")
            
            # Load data - use sample data if in GCP and no dataset specified
            if USE_GCP and gcp_config.dataset_bucket:
                # Try to download from GCS
                local_path = gcp_config.download_dataset('sample_data.csv')
                if local_path and os.path.exists(local_path):
                    data_df = pd.read_csv(local_path)
                else:
                    # Generate sample data
                    data_df = data_retriever.fetch_data(confirmed_codes, sample_size=1000)
            else:
                # Generate sample data
                data_df = data_retriever.fetch_data(confirmed_codes, sample_size=1000)
            
            # Apply clustering
            result_df = audience_builder.build_audience("", confirmed_codes, data_df)
            profiles = audience_builder.get_group_profiles()
            
            # Convert to JSON-serializable format
            result_json = result_df.head(100).to_dict('records')
            
            # Calculate group statistics
            group_stats = result_df.groupby('Group').size().to_dict()
            total_records = len(result_df)
            
            # Format response
            segments = []
            for group_id, profile in profiles.items():
                segment = {
                    'id': int(group_id),
                    'name': f'Segment {group_id + 1}',
                    'size': group_stats.get(group_id, 0),
                    'percentage': round(group_stats.get(group_id, 0) / total_records * 100, 2),
                    'characteristics': profile['characteristics']
                }
                segments.append(segment)
            
            return jsonify({
                'status': 'success',
                'segments': segments,
                'total_records': total_records,
                'sample_data': result_json
            })
            
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
            
    except Exception as e:
        print(f"Error in process_audience: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/variables/catalog', methods=['GET'])
@cache_result(expiration=3600)  # Cache for 1 hour
def get_variable_catalog():
    """Get the full variable catalog"""
    catalog = variable_selector.get_catalog()
    return jsonify({
        'status': 'success',
        'catalog': catalog,
        'count': len(catalog)
    })

@app.route('/api/data/sample', methods=['GET'])
def get_sample_data():
    """Get sample data for testing"""
    sample_variables = ['AGE_RANGE', 'INCOME_LEVEL', 'LOCATION_TYPE']
    sample_df = data_retriever.fetch_data(sample_variables, sample_size=100)
    
    return jsonify({
        'status': 'success',
        'data': sample_df.to_dict('records'),
        'shape': sample_df.shape
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # This is used by App Engine
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))