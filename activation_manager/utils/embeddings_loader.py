"""
Utility for loading and managing variable embeddings.
"""

import os
import shutil
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmbeddingsLoader:
    """Manages loading and copying embeddings files to the project."""
    
    @staticmethod
    def setup_embeddings(source_dir: str, target_dir: Optional[str] = None) -> dict:
        """
        Copy embeddings files from source to project directory.
        
        Args:
            source_dir: Directory containing the embeddings files
            target_dir: Target directory (defaults to project data dir)
            
        Returns:
            Dictionary with paths to copied files
        """
        if target_dir is None:
            # Default to project data directory
            project_root = Path(__file__).parent.parent.parent
            target_dir = project_root / "data" / "embeddings"
        else:
            target_dir = Path(target_dir)
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Files to copy
        files_to_copy = {
            'embeddings': 'variable_vectors_enhanced.parquet',
            'enriched_data': 'variable_catalogue_enhanced.jsonl',
            'fallback_embeddings': 'variable_vectors.parquet',
            'fallback_enriched': 'enriched_variables.jsonl'
        }
        
        copied_files = {}
        source_path = Path(source_dir)
        
        for key, filename in files_to_copy.items():
            source_file = source_path / filename
            if source_file.exists():
                target_file = target_dir / filename
                logger.info(f"Copying {filename} to {target_file}")
                shutil.copy2(source_file, target_file)
                copied_files[key] = str(target_file)
            else:
                logger.warning(f"Source file not found: {source_file}")
        
        # Create config file
        config_file = target_dir / "embeddings_config.json"
        import json
        with open(config_file, 'w') as f:
            json.dump({
                'embeddings_path': copied_files.get('embeddings'),
                'enriched_data_path': copied_files.get('enriched_data'),
                'fallback_embeddings_path': copied_files.get('fallback_embeddings'),
                'fallback_enriched_path': copied_files.get('fallback_enriched'),
                'embedding_dim': 1536,
                'model': 'text-embedding-ada-002'
            }, f, indent=2)
        
        copied_files['config'] = str(config_file)
        
        logger.info(f"Embeddings setup complete. Files copied to {target_dir}")
        return copied_files
    
    @staticmethod
    def get_embeddings_config() -> dict:
        """Get embeddings configuration."""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "data" / "embeddings" / "embeddings_config.json"
        
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    @staticmethod
    def verify_embeddings() -> bool:
        """Verify that embeddings are properly set up."""
        config = EmbeddingsLoader.get_embeddings_config()
        
        if not config:
            return False
        
        required_files = ['embeddings_path', 'enriched_data_path']
        for key in required_files:
            if key not in config or not Path(config[key]).exists():
                logger.error(f"Missing required embeddings file: {key}")
                return False
        
        return True