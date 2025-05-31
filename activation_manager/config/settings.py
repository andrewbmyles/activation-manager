"""
Configuration settings for Activation Manager
Supports both local and GCP environments
"""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings with environment-based configuration"""
    
    def __init__(self):
        # Base paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.activation_manager_dir = self.base_dir / "activation_manager"
        
        # Environment
        self.env = os.getenv('FLASK_ENV', 'development')
        self.is_production = os.getenv('GAE_ENV', '').startswith('standard')
        
        # API Keys (from environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Database settings
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///activation_manager.db')
        
        # Embeddings path
        self.embeddings_path = self._get_embeddings_path()
        
        # Server settings
        self.port = int(os.getenv('PORT', 8080))
        self.host = '0.0.0.0'
        self.debug = self.env == 'development'
        
        # CORS settings
        self.cors_origins = self._get_cors_origins()
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Feature flags
        self.use_embeddings = os.getenv('USE_EMBEDDINGS', 'true').lower() == 'true'
        self.use_nlweb = os.getenv('USE_NLWEB', 'false').lower() == 'true'
        
        # Clustering settings
        self.min_cluster_size_pct = 0.05  # 5%
        self.max_cluster_size_pct = 0.10  # 10%
        
        # Export settings
        self.export_chunk_size = 10000
        
        # Session settings
        self.session_timeout_minutes = 30
        
    def _get_embeddings_path(self) -> Path:
        """Get the appropriate embeddings path based on environment"""
        if self.is_production:
            # In GCP, embeddings should be in the app directory
            return self.activation_manager_dir / "data" / "embeddings"
        else:
            # Local development - check multiple possible locations
            possible_paths = [
                self.activation_manager_dir / "data" / "embeddings",
                self.base_dir / "data" / "embeddings",
                Path("/Users/myles/Documents/Activation Manager/data/embeddings")
            ]
            
            for path in possible_paths:
                if path.exists():
                    return path
            
            # Default to activation_manager path
            return self.activation_manager_dir / "data" / "embeddings"
    
    def _get_cors_origins(self) -> list:
        """Get CORS origins based on environment"""
        if self.is_production:
            return [
                'https://activation-manager.appspot.com',
                'https://*.appspot.com',
                'https://activation-manager.web.app',
                'https://*.firebaseapp.com'
            ]
        else:
            # Allow all origins in development
            return ['*']
    
    def get_variable_data_path(self) -> Optional[Path]:
        """Get path to variable data files"""
        # Check for enriched variables file
        enriched_path = Path("/Users/myles/Documents/NL Variable Parser and Suggestion/enriched_variables.jsonl")
        if enriched_path.exists():
            return enriched_path
        
        # Check for variables in embeddings directory
        embeddings_vars = self.embeddings_path / "variables_full.json"
        if embeddings_vars.exists():
            return embeddings_vars
        
        return None
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary for debugging"""
        return {
            'env': self.env,
            'is_production': self.is_production,
            'port': self.port,
            'debug': self.debug,
            'embeddings_path': str(self.embeddings_path),
            'use_embeddings': self.use_embeddings,
            'use_nlweb': self.use_nlweb,
            'cors_origins': self.cors_origins
        }

# Legacy compatibility - export individual settings
settings = Settings()
BASE_DIR = str(settings.base_dir)
ACTIVATION_MANAGER_DIR = str(settings.activation_manager_dir)
API_HOST = settings.host
API_PORT = settings.port
API_DEBUG = settings.debug
MIN_CLUSTER_SIZE_PCT = settings.min_cluster_size_pct
MAX_CLUSTER_SIZE_PCT = settings.max_cluster_size_pct
EXPORT_CHUNK_SIZE = settings.export_chunk_size
SESSION_TIMEOUT_MINUTES = settings.session_timeout_minutes

# Add missing synthetic data path for legacy compatibility
SYNTHETIC_DATA_PATH = str(settings.base_dir / "Synthetic_Data" / "output" / "synthetic_consumer_data_100000_20250525_155847.csv")