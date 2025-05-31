"""
API endpoints for persisting and retrieving user data (audiences, platforms, distributions).
Supports both BigQuery and Parquet file storage backends.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import handlers based on configured backend
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'parquet')  # 'parquet' or 'bigquery'

if STORAGE_BACKEND == 'parquet':
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_persistence.parquet_handlers import (
        AudienceHandler, PlatformHandler, DistributionHandler
    )
else:
    # Import BigQuery handlers (to be implemented)
    from data_persistence.bigquery_handlers import (
        AudienceHandler, PlatformHandler, DistributionHandler
    )

app = Flask(__name__)
CORS(app)

# Initialize handlers
audience_handler = AudienceHandler()
platform_handler = PlatformHandler()
distribution_handler = DistributionHandler()


# Audience endpoints
@app.route('/api/audiences', methods=['POST'])
def save_audience():
    """Save a new audience or update existing one."""
    try:
        data = request.json
        
        # Validate required fields
        required = ['user_id', 'name', 'data_type', 'selected_variables']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Save audience
        audience_id = audience_handler.save_audience(data)
        
        return jsonify({
            'success': True,
            'audience_id': audience_id,
            'message': 'Audience saved successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audiences/<audience_id>', methods=['GET'])
def get_audience(audience_id):
    """Get a specific audience by ID."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        audience = audience_handler.get_audience(audience_id, user_id)
        
        if audience:
            return jsonify({
                'success': True,
                'audience': audience
            }), 200
        else:
            return jsonify({'error': 'Audience not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audiences', methods=['GET'])
def list_audiences():
    """List audiences for a user."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        audiences = audience_handler.list_audiences(user_id, status, limit)
        
        return jsonify({
            'success': True,
            'audiences': audiences,
            'count': len(audiences)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audiences/<audience_id>/status', methods=['PUT'])
def update_audience_status(audience_id):
    """Update audience status (archive, activate, etc.)."""
    try:
        data = request.json
        user_id = data.get('user_id')
        status = data.get('status')
        
        if not user_id or not status:
            return jsonify({'error': 'user_id and status required'}), 400
        
        if status not in ['draft', 'active', 'archived']:
            return jsonify({'error': 'Invalid status'}), 400
        
        success = audience_handler.update_audience_status(audience_id, user_id, status)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Audience status updated to {status}'
            }), 200
        else:
            return jsonify({'error': 'Audience not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Platform endpoints
@app.route('/api/platforms', methods=['POST'])
def save_platform():
    """Save a new platform configuration."""
    try:
        data = request.json
        
        # Validate required fields
        required = ['user_id', 'platform_type', 'name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # TODO: Encrypt credentials before saving
        if 'credentials' in data:
            # Encrypt credentials here
            pass
        
        # Save platform
        platform_id = platform_handler.save_platform(data)
        
        return jsonify({
            'success': True,
            'platform_id': platform_id,
            'message': 'Platform saved successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/platforms/<platform_id>', methods=['GET'])
def get_platform(platform_id):
    """Get a specific platform by ID."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        platform = platform_handler.get_platform(platform_id, user_id)
        
        if platform:
            # TODO: Decrypt credentials before returning
            return jsonify({
                'success': True,
                'platform': platform
            }), 200
        else:
            return jsonify({'error': 'Platform not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/platforms', methods=['GET'])
def list_platforms():
    """List platforms for a user."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        platform_type = request.args.get('platform_type')
        status = request.args.get('status', 'active')
        
        platforms = platform_handler.list_platforms(user_id, platform_type, status)
        
        # Remove sensitive credentials from list view
        for platform in platforms:
            if 'credentials' in platform:
                platform['credentials'] = {'encrypted': True}
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'count': len(platforms)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Distribution endpoints
@app.route('/api/distributions', methods=['POST'])
def create_distribution():
    """Create a new distribution."""
    try:
        data = request.json
        
        # Validate required fields
        required = ['user_id', 'audience_id', 'platform_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Set default values
        data['status'] = data.get('status', 'scheduled')
        data['distribution_type'] = data.get('distribution_type', 'initial')
        
        # Save distribution
        distribution_id = distribution_handler.save_distribution(data)
        
        # TODO: Trigger actual distribution process
        
        return jsonify({
            'success': True,
            'distribution_id': distribution_id,
            'message': 'Distribution created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/distributions/<distribution_id>', methods=['GET'])
def get_distribution(distribution_id):
    """Get a specific distribution by ID."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        distribution = distribution_handler.get_distribution(distribution_id, user_id)
        
        if distribution:
            return jsonify({
                'success': True,
                'distribution': distribution
            }), 200
        else:
            return jsonify({'error': 'Distribution not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audiences/<audience_id>/distributions', methods=['GET'])
def list_distributions_for_audience(audience_id):
    """List distributions for a specific audience."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        limit = int(request.args.get('limit', 10))
        
        distributions = distribution_handler.list_distributions_for_audience(
            audience_id, user_id, limit
        )
        
        return jsonify({
            'success': True,
            'distributions': distributions,
            'count': len(distributions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/distributions/<distribution_id>/status', methods=['PUT'])
def update_distribution_status(distribution_id):
    """Update distribution status and results."""
    try:
        data = request.json
        user_id = data.get('user_id')
        status = data.get('status')
        
        if not user_id or not status:
            return jsonify({'error': 'user_id and status required'}), 400
        
        match_results = data.get('match_results')
        error_details = data.get('error_details')
        
        success = distribution_handler.update_distribution_status(
            distribution_id, user_id, status, match_results, error_details
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Distribution status updated to {status}'
            }), 200
        else:
            return jsonify({'error': 'Distribution not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Summary endpoints
@app.route('/api/users/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    """Get summary statistics for a user."""
    try:
        # Get counts
        audiences = audience_handler.list_audiences(user_id, limit=1000)
        platforms = platform_handler.list_platforms(user_id)
        
        # Count by status
        audience_stats = {
            'total': len(audiences),
            'active': sum(1 for a in audiences if a.get('status') == 'active'),
            'draft': sum(1 for a in audiences if a.get('status') == 'draft'),
            'archived': sum(1 for a in audiences if a.get('status') == 'archived')
        }
        
        platform_stats = {
            'total': len(platforms),
            'active': sum(1 for p in platforms if p.get('status') == 'active'),
            'by_type': {}
        }
        
        # Count by platform type
        for platform in platforms:
            ptype = platform.get('platform_type', 'unknown')
            platform_stats['by_type'][ptype] = platform_stats['by_type'].get(ptype, 0) + 1
        
        return jsonify({
            'success': True,
            'summary': {
                'audiences': audience_stats,
                'platforms': platform_stats,
                'last_activity': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'storage_backend': STORAGE_BACKEND,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True)