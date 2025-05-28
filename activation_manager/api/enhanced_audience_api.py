"""
Enhanced Audience API with all requested features
Supports data type selection, CSV export, and enhanced workflow
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import io
import csv
from typing import Dict, Any, List, Optional
import uuid

# Import our enhanced modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_variable_selector_v2 import EnhancedVariableSelectorV2
from core.enhanced_variable_selector_v3 import EnhancedVariableSelectorV3
from core.audience_builder import DataRetriever, ConstrainedKMedians
from core.prizm_analyzer import PRIZMAnalyzer
from config.settings import SYNTHETIC_DATA_PATH, API_HOST, API_PORT, API_DEBUG

# Define WorkflowState locally
class WorkflowState:
    """Maintains state throughout the workflow process"""
    def __init__(self):
        self.current_step = "initial"
        self.user_prompt = ""
        self.parsed_requirements = {}
        self.suggested_variables = []
        self.confirmed_variables = []
        self.data = None
        self.segments = []
        self.timestamp = datetime.now()

app = Flask(__name__)
CORS(app)

# Session storage
sessions = {}

# Initialize components
# Try V4 with real-time embeddings first, then V3, then V2
try:
    from core.enhanced_variable_selector_v4 import EnhancedVariableSelectorV4
    variable_selector = EnhancedVariableSelectorV4(use_embeddings=True)
    print("✅ Using Enhanced Variable Selector V4 with real-time query embeddings")
except Exception as e:
    print(f"⚠️  Failed to load V4: {e}")
    try:
        variable_selector = EnhancedVariableSelectorV3(use_embeddings=True)
        print("✅ Using Enhanced Variable Selector V3 with embeddings support")
    except Exception as e2:
        print(f"⚠️  Failed to load V3 with embeddings: {e2}")
        variable_selector = EnhancedVariableSelectorV2()
        print("ℹ️  Using Enhanced Variable Selector V2 with TF-IDF")
data_retriever = DataRetriever()
# Load the 100k dataset
data_retriever.load_data(SYNTHETIC_DATA_PATH)
clusterer = ConstrainedKMedians()
prizm_analyzer = PRIZMAnalyzer()

# Data loading status
try:
    print(f"✅ Loaded synthetic data with {len(data_retriever.data)} records from: {SYNTHETIC_DATA_PATH}")
except Exception as e:
    print(f"⚠️ Warning: Could not load data: {e}")

class EnhancedWorkflowState(WorkflowState):
    """Extended workflow state with data type information"""
    def __init__(self):
        super().__init__()
        self.data_type = None  # 'first_party', 'third_party', 'clean_room'
        self.subtype = None    # Specific subtype like 'rampid', 'uid2', etc.
        self.audience_id = None
        self.export_ready = False

def generate_descriptive_segment_names(segments: List[Dict], user_query: str) -> List[Dict]:
    """Generate descriptive names for segments based on characteristics"""
    
    # Keywords for naming
    name_templates = {
        'high_value': ['Premium', 'VIP', 'Elite', 'High-Value'],
        'engaged': ['Active', 'Engaged', 'Loyal', 'Frequent'],
        'new': ['New', 'Recent', 'First-Time', 'Novice'],
        'tech': ['Digital', 'Tech-Savvy', 'Connected', 'Online'],
        'eco': ['Eco-Conscious', 'Green', 'Sustainable', 'Environmental'],
        'urban': ['Urban', 'Metro', 'City', 'Downtown'],
        'family': ['Family', 'Parents', 'Household', 'Family-Oriented'],
        'young': ['Young', 'Millennial', 'Gen-Z', 'Youth'],
        'affluent': ['Affluent', 'Wealthy', 'Premium', 'Luxury']
    }
    
    # Extract keywords from query
    query_lower = user_query.lower()
    matched_categories = []
    
    for key, values in name_templates.items():
        if any(term in query_lower for term in [key] + [v.lower() for v in values]):
            matched_categories.append(key)
    
    # Generate names for each segment
    for i, segment in enumerate(segments):
        base_names = []
        
        # Use matched categories
        for cat in matched_categories[:2]:  # Use top 2 matches
            base_names.append(name_templates[cat][i % len(name_templates[cat])])
        
        # Add segment-specific suffix
        suffixes = ['Leaders', 'Advocates', 'Enthusiasts', 'Pioneers', 'Champions']
        
        if base_names:
            segment['name'] = f"{' '.join(base_names)} {suffixes[i % len(suffixes)]}"
        else:
            # Fallback names
            fallback = ['Core Audience', 'Target Market', 'Key Segment', 'Primary Group', 'Focus Audience']
            segment['name'] = fallback[i % len(fallback)]
        
        # Add dominant traits
        segment['dominantTraits'] = extract_dominant_traits(segment)
    
    return segments

def extract_dominant_traits(segment: Dict) -> List[str]:
    """Extract dominant characteristics from a segment"""
    traits = []
    
    if 'characteristics' in segment:
        chars = segment['characteristics']
        
        # Find most common categorical values
        for key, value in chars.items():
            if isinstance(value, dict) and 'dominant_value' in value:
                if value['dominant_percentage'] > 60:  # If >60% share this trait
                    traits.append(f"{key}: {value['dominant_value']}")
        
        # Add numeric insights
        for key, value in chars.items():
            if isinstance(value, dict) and 'mean' in value:
                if 'income' in key.lower() and value.get('mean', 0) > 75000:
                    traits.append('High Income')
                elif 'age' in key.lower() and value.get('mean', 0) < 35:
                    traits.append('Young Adults')
    
    return traits[:3]  # Return top 3 traits

@app.route('/api/nl/start_session', methods=['POST'])
def start_session():
    """Initialize a new NL workflow session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = EnhancedWorkflowState()
    
    return jsonify({
        'session_id': session_id,
        'status': 'ready',
        'message': 'Session initialized'
    })

@app.route('/api/nl/process', methods=['POST'])
def process_nl_request():
    """Process natural language requests with enhanced workflow"""
    data = request.json
    session_id = data.get('session_id')
    action = data.get('action', 'process')
    payload = data.get('payload', {})
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    state = sessions[session_id]
    
    # Store data type if provided
    if 'data_type' in payload:
        state.data_type = payload['data_type']
    if 'subtype' in payload:
        state.subtype = payload['subtype']
    
    user_input = payload.get('input', '')
    
    # Debug logging
    print(f"Processing action: {action}, step: {state.current_step}, payload: {payload}")
    
    try:
        if action == 'process':
            if state.current_step in ['initial', 'awaiting_input']:
                # Analyze the prompt
                state.user_prompt = user_input
                suggested = variable_selector.analyze_request(user_input, top_n=15)
                
                # Group by type
                grouped_vars = {}
                for var in suggested:
                    var_type = var['type']
                    if var_type not in grouped_vars:
                        grouped_vars[var_type] = []
                    
                    # Add data availability info
                    var['dataAvailability'] = {
                        'first_party': True,  # Simplified for demo
                        'third_party': var_type in ['demographic', 'psychographic'],
                        'clean_room': var_type == 'behavioral'
                    }
                    
                    grouped_vars[var_type].append(var)
                
                state.suggested_variables = suggested
                state.current_step = 'variables_suggested'
                
                return jsonify({
                    'status': 'variables_suggested',
                    'suggested_variables': grouped_vars,
                    'total_suggested': len(suggested),
                    'session_id': session_id,
                    'data_type': state.data_type
                })
                
            elif state.current_step == 'variables_suggested' and action == 'process':
                # Handle variable confirmation
                confirmed_codes = payload.get('confirmed_variables', [])
                
                # If no confirmed variables explicitly passed, check the input
                if not confirmed_codes and ('use these variables' in user_input.lower() or 'confirm' in user_input.lower()):
                    # Extract variable codes
                    confirmed_codes = []
                    for var in state.suggested_variables:
                        if var['code'] in user_input or var['code'].lower() in user_input.lower():
                            confirmed_codes.append(var['code'])
                
                # If no specific codes, use top ones
                if not confirmed_codes and state.suggested_variables:
                    confirmed_codes = [v['code'] for v in state.suggested_variables[:7]]
                
                # Fetch data and cluster
                data_df = data_retriever.fetch_data(confirmed_codes)
                
                if data_df.empty:
                    return jsonify({'error': 'No data available'}), 400
                
                # Apply clustering
                cluster_labels = clusterer.fit_predict(data_df)
                data_df['Group'] = cluster_labels
                
                # Calculate statistics
                result_df = data_df.sort_values('Group').reset_index(drop=True)
                group_stats = result_df.groupby('Group').size()
                group_pcts = (group_stats / len(result_df) * 100).round(2)
                
                # Create segments with descriptive names
                segments = []
                for group_id in sorted(result_df['Group'].unique()):
                    group_data = result_df[result_df['Group'] == group_id]
                    
                    segment = {
                        'group_id': int(group_id),
                        'size': len(group_data),
                        'size_percentage': float(group_pcts[group_id]),
                        'characteristics': analyze_group_characteristics(group_data)
                    }
                    
                    # Add PRIZM if available
                    if 'PRIZM_SEGMENT' in group_data.columns:
                        prizm_info = prizm_analyzer.analyze_segment_distribution(group_data)
                        if 'segment_profiles' in prizm_info and str(group_id) in prizm_info['segment_profiles']:
                            segment['prizm_profile'] = prizm_info['segment_profiles'][str(group_id)]
                    
                    segments.append(segment)
                
                # Generate descriptive names
                segments = generate_descriptive_segment_names(segments, state.user_prompt)
                
                # Store results
                audience_id = str(uuid.uuid4())
                state.audience_id = audience_id
                state.segments = segments
                state.data = result_df
                state.current_step = 'complete'
                state.export_ready = True
                
                # Store for export
                sessions[audience_id] = state  # Also store by audience_id for export
                
                return jsonify({
                    'status': 'complete',
                    'segments': segments,
                    'total_records': len(result_df),
                    'variables_used': confirmed_codes,
                    'audience_id': audience_id,
                    'data_type': state.data_type,
                    'message': f'Successfully created {len(segments)} segments'
                })
        
        elif action == 'confirm':
            # Handle explicit variable confirmation
            confirmed_codes = payload.get('confirmed_variables', [])
            
            if not confirmed_codes:
                return jsonify({'error': 'No variables to confirm'}), 400
            
            print(f"Confirming variables: {confirmed_codes}")
            
            # Fetch data and cluster
            data_df = data_retriever.fetch_data(confirmed_codes)
            
            if data_df.empty:
                return jsonify({'error': 'No data available for selected variables'}), 400
            
            print(f"Fetched data shape: {data_df.shape}")
            
            # Apply clustering
            cluster_labels = clusterer.fit_predict(data_df)
            data_df['Group'] = cluster_labels
            
            # Calculate statistics
            result_df = data_df.sort_values('Group').reset_index(drop=True)
            group_stats = result_df.groupby('Group').size()
            group_pcts = (group_stats / len(result_df) * 100).round(2)
            
            # Create segments with descriptive names
            segments = []
            for group_id in sorted(result_df['Group'].unique()):
                group_data = result_df[result_df['Group'] == group_id]
                
                segment = {
                    'group_id': int(group_id),
                    'size': len(group_data),
                    'size_percentage': float(group_pcts[group_id]),
                    'characteristics': analyze_group_characteristics(group_data)
                }
                
                # Add PRIZM if available
                if 'PRIZM_SEGMENT' in group_data.columns:
                    prizm_info = prizm_analyzer.analyze_segment_distribution(group_data)
                    if 'segment_profiles' in prizm_info and str(group_id) in prizm_info['segment_profiles']:
                        segment['prizm_profile'] = prizm_info['segment_profiles'][str(group_id)]
                
                segments.append(segment)
            
            # Generate descriptive names
            segments = generate_descriptive_segment_names(segments, state.user_prompt)
            
            # Store results
            audience_id = str(uuid.uuid4())
            state.audience_id = audience_id
            state.segments = segments
            state.data = result_df
            state.current_step = 'complete'
            state.export_ready = True
            
            # Store for export
            sessions[audience_id] = state  # Also store by audience_id for export
            
            return jsonify({
                'status': 'complete',
                'segments': segments,
                'total_records': len(result_df),
                'variables_used': confirmed_codes,
                'audience_id': audience_id,
                'data_type': state.data_type,
                'message': f'Successfully created {len(segments)} segments'
            })
        
        return jsonify({'error': 'Unknown action'}), 400
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

def analyze_group_characteristics(group_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze characteristics of a group"""
    characteristics = {}
    
    for col in group_data.columns:
        if col == 'Group':
            continue
            
        if group_data[col].dtype == 'object' or group_data[col].dtype == 'category':
            # Categorical variable
            value_counts = group_data[col].value_counts()
            mode_value = value_counts.index[0] if len(value_counts) > 0 else 'Unknown'
            mode_pct = (value_counts.iloc[0] / len(group_data) * 100) if len(value_counts) > 0 else 0
            
            characteristics[col] = {
                'type': 'categorical',
                'dominant_value': str(mode_value),
                'dominant_percentage': round(mode_pct, 1),
                'distribution': value_counts.head(5).to_dict()
            }
        else:
            # Numeric variable
            characteristics[col] = {
                'type': 'numeric',
                'mean': round(float(group_data[col].mean()), 2),
                'median': round(float(group_data[col].median()), 2),
                'std': round(float(group_data[col].std()), 2),
                'min': round(float(group_data[col].min()), 2),
                'max': round(float(group_data[col].max()), 2)
            }
    
    return characteristics

@app.route('/api/export/<audience_id>', methods=['GET'])
def export_audience(audience_id):
    """Export audience data as CSV"""
    format_type = request.args.get('format', 'csv')
    
    # Check both session storage locations
    if audience_id not in sessions:
        # Try to find by session_id
        state = None
        for sid, s in sessions.items():
            if hasattr(s, 'audience_id') and s.audience_id == audience_id:
                state = s
                break
        
        if not state:
            return jsonify({'error': 'Audience not found'}), 404
    else:
        state = sessions[audience_id]
    
    if not hasattr(state, 'data') or state.data is None:
        return jsonify({'error': 'No data available for export'}), 400
    
    if format_type == 'csv':
        # Create CSV with additional metadata
        output = io.StringIO()
        
        # Write metadata
        output.write(f"# Audience Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"# Query: {getattr(state, 'user_prompt', 'N/A')}\n")
        output.write(f"# Data Type: {getattr(state, 'data_type', 'N/A')}\n")
        output.write(f"# Total Records: {len(state.data)}\n")
        output.write(f"# Segments: {len(getattr(state, 'segments', []))}\n")
        output.write("#\n")
        
        # Write segment summary
        if hasattr(state, 'segments'):
            output.write("# Segment Summary:\n")
            for seg in state.segments:
                segment_name = seg.get('name', f"Segment {seg['group_id']}")
                output.write(f"# - {segment_name}: {seg['size']} records ({seg['size_percentage']:.1f}%)\n")
            output.write("#\n")
        
        # Write data
        state.data.to_csv(output, index=False)
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=audience_{audience_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
    
    return jsonify({'error': 'Unsupported format'}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'components': {
            'variable_selector': 'ready',
            'data_retriever': 'ready' if data_retriever.data is not None else 'no_data',
            'sessions_active': len(sessions)
        }
    })

@app.route('/api/distribute', methods=['POST'])
def distribute_audience():
    """Handle audience distribution to platforms"""
    data = request.json
    audience_id = data.get('audience_id')
    platforms = data.get('platforms', [])
    
    # Simulate distribution process
    results = []
    for platform in platforms:
        results.append({
            'platform': platform,
            'status': 'success',
            'records_sent': np.random.randint(50000, 150000),
            'match_rate': round(np.random.uniform(0.6, 0.95), 2)
        })
    
    return jsonify({
        'status': 'success',
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"🚀 Starting Enhanced Audience API on {API_HOST}:{API_PORT}...")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)