"""
Vercel serverless function entry point for the Enhanced Audience API
"""
import sys
import os

# Add the activation_manager directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../activation_manager'))

from activation_manager.api.enhanced_audience_api import app

# Vercel expects a callable named 'app'
handler = app