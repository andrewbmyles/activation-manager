# GCP Cloud Run entry point
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the enhanced Flask app for GCP
try:
    from api.gcp_enhanced_api import app
except ImportError:
    # Fallback to regular enhanced API
    from api.enhanced_audience_api import app

# Cloud Run uses PORT environment variable
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))