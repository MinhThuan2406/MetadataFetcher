"""
Cache manager for the unified MetadataFetcher architecture.
Provides caching for API responses, metadata results, and configuration.
"""

import json
import os
import hashlib
import time
from typing import Any, Optional, Dict, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching for the MetadataFetcher system.
    """
    
    def __init__(self, cache_directory: str = "cache", default_ttl: int = 86400):
        """
        Initialize the cache manager.
        
        Args:
            cache_directory: Directory to store cache files
            default_ttl: Default time-to-live in seconds (24 hours)
        """
        self.cache_directory = Path(cache_directory)
        self.default_ttl = default_ttl
        self.cache_directory.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.cache_directory / "api").mkdir(exist_ok=True)
        (self.cache_directory / "metadata").mkdir(exist_ok=True)
        (self.cache_directory / "config").mkdir(exist_ok=True)
    
    def _get_cache_key(self, key: str, prefix: str = "") -> str:
        """Generate a cache key with optional prefix."""
        if prefix:
            return f"{prefix}_{key}"
        return key
    
    def _get_cache_path(self, key: str, cache_type: str = "api") -> Path:
        """Get the file path for a cache entry."""
        # Create a hash of the key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_directory / cache_type / f"{key_hash}.json"
    
    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cache data is expired."""
        if 'timestamp' not in cache_data:
            return True
        
        ttl = cache_data.get('ttl', self.default_ttl)
        age = time.time() - cache_data['timestamp']
        return age > ttl
    
    def get(self, key: str, cache_type: str = "api") -> Optional[Any]:
        """
        Get cached data.
        
        Args:
            key: Cache key
            cache_type: Type of cache (api, metadata, config)
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(key, cache_type)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if self._is_expired(cache_data):
                logger.debug(f"Cache expired for key: {key}")
                cache_path.unlink()  # Remove expired cache
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_data.get('data')
            
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error reading cache for key {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, cache_type: str = "api", ttl: Optional[int] = None) -> None:
        """
        Set cached data.
        
        Args:
            key: Cache key
            data: Data to cache
            cache_type: Type of cache (api, metadata, config)
            ttl: Time-to-live in seconds (uses default if None)
        """
        cache_path = self._get_cache_path(key, cache_type)
        
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl,
            'key': key
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cached data for key: {key}")
            
        except IOError as e:
            logger.warning(f"Error writing cache for key {key}: {e}")
    
    def delete(self, key: str, cache_type: str = "api") -> bool:
        """
        Delete cached data.
        
        Args:
            key: Cache key
            cache_type: Type of cache
            
        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(key, cache_type)
        
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Deleted cache for key: {key}")
            return True
        
        return False
    
    def clear(self, cache_type: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            cache_type: Type of cache to clear (None for all)
            
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        if cache_type:
            cache_dir = self.cache_directory / cache_type
            if cache_dir.exists():
                for cache_file in cache_dir.glob("*.json"):
                    cache_file.unlink()
                    cleared_count += 1
        else:
            # Clear all cache types
            for cache_dir in self.cache_directory.iterdir():
                if cache_dir.is_dir():
                    for cache_file in cache_dir.glob("*.json"):
                        cache_file.unlink()
                        cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} cache entries")
        return cleared_count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        for cache_dir in self.cache_directory.iterdir():
            if cache_dir.is_dir():
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if self._is_expired(cache_data):
                            cache_file.unlink()
                            removed_count += 1
                            
                    except (json.JSONDecodeError, IOError):
                        # Remove corrupted cache files
                        cache_file.unlink()
                        removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'expired_files': 0,
            'cache_types': {}
        }
        
        for cache_dir in self.cache_directory.iterdir():
            if cache_dir.is_dir():
                cache_type = cache_dir.name
                type_stats = {
                    'files': 0,
                    'size': 0,
                    'expired': 0
                }
                
                for cache_file in cache_dir.glob("*.json"):
                    type_stats['files'] += 1
                    type_stats['size'] += cache_file.stat().st_size
                    
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if self._is_expired(cache_data):
                            type_stats['expired'] += 1
                            
                    except (json.JSONDecodeError, IOError):
                        type_stats['expired'] += 1
                
                stats['cache_types'][cache_type] = type_stats
                stats['total_files'] += type_stats['files']
                stats['total_size'] += type_stats['size']
                stats['expired_files'] += type_stats['expired']
        
        return stats 