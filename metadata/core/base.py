"""
Abstract base class for all fetchers in the unified architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from .schema import UnifiedMetadata, ToolCategory
from .config import FetcherConfig
from .cache import CacheManager
import time
import logging

logger = logging.getLogger(__name__)

class FetcherError(Exception):
    """Base exception for fetcher errors."""
    pass

class RateLimitError(FetcherError):
    """Rate limit exceeded."""
    pass

class DataSourceError(FetcherError):
    """Data source unavailable."""
    pass

class BaseFetcher(ABC):
    """
    Abstract base class for all fetchers.
    
    Provides a unified interface and common functionality for fetching
    metadata from various data sources.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        """
        Initialize the fetcher.
        
        Args:
            config: Configuration object for the fetcher
        """
        self.config = config or FetcherConfig()
        self.name = self.__class__.__name__
        self.start_time = None
        self.end_time = None
        self.cache_manager = CacheManager(
            cache_directory=self.config.cache_directory,
            default_ttl=self.config.cache_ttl
        )
    
    @abstractmethod
    def can_fetch(self, tool_name: str) -> bool:
        """
        Check if this fetcher can handle the given tool.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if this fetcher can handle the tool
        """
        pass
    
    @abstractmethod
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """
        Fetch metadata for a tool.
        
        Args:
            tool_name: Name of the tool to fetch metadata for
            
        Returns:
            UnifiedMetadata object or None if not found
        """
        pass
    
    def fetch_with_timing(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """
        Fetch metadata with timing information.
        
        Args:
            tool_name: Name of the tool to fetch metadata for
            
        Returns:
            UnifiedMetadata object with timing information
        """
        self.start_time = time.time()
        
        try:
            metadata = self.fetch(tool_name)
            
            if metadata:
                self.end_time = time.time()
                metadata.fetch_duration = self.end_time - self.start_time
                metadata.sources.append(self.name.lower())
                
                logger.info(f"{self.name} fetched metadata for {tool_name} "
                          f"in {metadata.fetch_duration:.2f}s")
            
            return metadata
            
        except Exception as e:
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            
            logger.error(f"{self.name} failed to fetch {tool_name} "
                        f"after {duration:.2f}s: {e}")
            raise
    
    def validate_metadata(self, metadata: UnifiedMetadata) -> bool:
        """
        Validate that the fetched metadata is complete and correct.
        
        Args:
            metadata: The metadata to validate
            
        Returns:
            True if metadata is valid
        """
        if not metadata:
            return False
        
        # Basic validation
        if not metadata.name:
            logger.warning(f"{self.name}: Metadata missing name")
            return False
        
        # Check for essential information
        has_essential_info = (
            metadata.description or 
            metadata.homepage or 
            metadata.documentation or
            metadata.installation_methods
        )
        
        if not has_essential_info:
            logger.warning(f"{self.name}: Metadata for {metadata.name} "
                          f"lacks essential information")
            return False
        
        return True
    
    def enrich_metadata(self, metadata: UnifiedMetadata, 
                       additional_data: Dict[str, Any]) -> UnifiedMetadata:
        """
        Enrich metadata with additional data.
        
        Args:
            metadata: The metadata to enrich
            additional_data: Additional data to merge
            
        Returns:
            Enriched metadata
        """
        if not additional_data:
            return metadata
        
        # Merge raw data
        metadata.raw_data.update(additional_data)
        
        # Update sources
        if 'source' in additional_data:
            metadata.sources.append(additional_data['source'])
        
        # Update category fields if provided
        if 'category_fields' in additional_data:
            metadata.category_fields.update(additional_data['category_fields'])
        
        return metadata
    
    def get_priority(self) -> int:
        """
        Get the priority of this fetcher.
        
        Lower numbers indicate higher priority.
        
        Returns:
            Priority value (lower is higher priority)
        """
        return 100  # Default priority
    
    def get_supported_categories(self) -> List[ToolCategory]:
        """
        Get the tool categories this fetcher supports.
        
        Returns:
            List of supported tool categories
        """
        return [ToolCategory.GENERIC]  # Default to generic
    
    def __str__(self) -> str:
        return f"{self.name}(priority={self.get_priority()})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})" 

    def _get_cached_response(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Get cached API response."""
        if not self.config.enable_caching:
            return None
        
        cache_key = f"{self.name}_{url}_{hash(str(headers))}"
        return self.cache_manager.get(cache_key, "api")
    
    def _cache_response(self, url: str, response_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> None:
        """Cache API response."""
        if not self.config.enable_caching:
            return
        
        cache_key = f"{self.name}_{url}_{hash(str(headers))}"
        self.cache_manager.set(cache_key, response_data, "api")
    
    def _get_cached_metadata(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Get cached metadata."""
        if not self.config.enable_caching:
            return None
        
        cache_key = f"{self.name}_{tool_name}"
        cached_data = self.cache_manager.get(cache_key, "metadata")
        
        if cached_data:
            return UnifiedMetadata.from_dict(cached_data)
        
        return None
    
    def _cache_metadata(self, tool_name: str, metadata: UnifiedMetadata) -> None:
        """Cache metadata."""
        if not self.config.enable_caching:
            return
        
        cache_key = f"{self.name}_{tool_name}"
        self.cache_manager.set(cache_key, metadata.to_dict(), "metadata") 