"""
Shared cache for variable data between workers
Uses file system as shared storage since App Engine doesn't support multiprocessing.shared_memory
"""

import os
import pickle
import logging
import hashlib
import time
from pathlib import Path
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class SharedCache:
    """File-based cache for sharing data between App Engine workers"""
    
    def __init__(self, cache_dir: str = "/tmp/activation_manager_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key"""
        # Hash key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def _get_lock_path(self, key: str) -> Path:
        """Get lock file path for a key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.lock"
        
    def get(self, key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Get cached data if it exists and is fresh"""
        try:
            cache_path = self._get_cache_path(key)
            lock_path = self._get_lock_path(key)
            
            # Skip if being written
            if lock_path.exists():
                logger.info(f"Cache key {key} is being written, skipping")
                return None
                
            if not cache_path.exists():
                return None
                
            # Check age
            stat = cache_path.stat()
            age = time.time() - stat.st_mtime
            if age > max_age_seconds:
                logger.info(f"Cache key {key} is stale ({age:.1f}s old), removing")
                cache_path.unlink(missing_ok=True)
                return None
                
            # Load data
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                
            logger.info(f"✅ Loaded {key} from cache (age: {age:.1f}s)")
            return data
            
        except Exception as e:
            logger.warning(f"Failed to load cache key {key}: {e}")
            return None
            
    def put(self, key: str, data: Any) -> bool:
        """Store data in cache"""
        try:
            cache_path = self._get_cache_path(key)
            lock_path = self._get_lock_path(key)
            
            # Create lock file
            lock_path.touch()
            
            try:
                # Write data
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
                    
                logger.info(f"✅ Cached {key}")
                return True
                
            finally:
                # Remove lock
                lock_path.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to cache key {key}: {e}")
            return False
            
    def clear(self) -> None:
        """Clear all cached data"""
        try:
            for file_path in self.cache_dir.glob("*.pkl"):
                file_path.unlink()
            for file_path in self.cache_dir.glob("*.lock"):
                file_path.unlink()
            logger.info("✅ Cleared cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

# Global cache instance
cache = SharedCache()