"""
Fetcher registry for managing and coordinating all data source fetchers.
"""

import logging
from typing import List, Optional, Dict, Any, Type
from .base import BaseFetcher
from .schema import UnifiedMetadata, ToolCategory
from .config import FetcherConfig
import time

logger = logging.getLogger(__name__)

class FetcherRegistry:
    """
    Registry for managing all available fetchers.
    
    Provides a centralized way to register, discover, and coordinate
    fetchers for different data sources.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        """
        Initialize the fetcher registry.
        
        Args:
            config: Configuration for the registry
        """
        self.config = config or FetcherConfig()
        self._fetchers: List[BaseFetcher] = []
        self._fetcher_map: Dict[str, BaseFetcher] = {}
        self._category_map: Dict[ToolCategory, List[BaseFetcher]] = {}
        
        # Initialize category map
        for category in ToolCategory:
            self._category_map[category] = []
    
    def register(self, fetcher: BaseFetcher) -> None:
        """
        Register a fetcher with the registry.
        
        Args:
            fetcher: The fetcher to register
        """
        if not isinstance(fetcher, BaseFetcher):
            raise ValueError(f"Fetcher must inherit from BaseFetcher: {type(fetcher)}")
        
        # Add to main list
        self._fetchers.append(fetcher)
        
        # Add to name map
        self._fetcher_map[fetcher.name] = fetcher
        
        # Add to category maps
        for category in fetcher.get_supported_categories():
            if category not in self._category_map:
                self._category_map[category] = []
            self._category_map[category].append(fetcher)
        
        # Sort fetchers by priority
        self._fetchers.sort(key=lambda f: f.get_priority())
        for category in self._category_map:
            self._category_map[category].sort(key=lambda f: f.get_priority())
        
        logger.info(f"Registered fetcher: {fetcher.name} (priority: {fetcher.get_priority()})")
    
    def register_class(self, fetcher_class: Type[BaseFetcher], 
                      config: Optional[FetcherConfig] = None) -> BaseFetcher:
        """
        Register a fetcher class and return the instance.
        
        Args:
            fetcher_class: The fetcher class to register
            config: Configuration for the fetcher
            
        Returns:
            The created fetcher instance
        """
        fetcher_config = config or self.config
        fetcher = fetcher_class(fetcher_config)
        self.register(fetcher)
        return fetcher
    
    def unregister(self, fetcher_name: str) -> bool:
        """
        Unregister a fetcher by name.
        
        Args:
            fetcher_name: Name of the fetcher to unregister
            
        Returns:
            True if fetcher was found and unregistered
        """
        if fetcher_name not in self._fetcher_map:
            return False
        
        fetcher = self._fetcher_map[fetcher_name]
        
        # Remove from main list
        if fetcher in self._fetchers:
            self._fetchers.remove(fetcher)
        
        # Remove from name map
        del self._fetcher_map[fetcher_name]
        
        # Remove from category maps
        for category in fetcher.get_supported_categories():
            if fetcher in self._category_map[category]:
                self._fetcher_map[category].remove(fetcher)
        
        logger.info(f"Unregistered fetcher: {fetcher_name}")
        return True
    
    def get_fetcher(self, name: str) -> Optional[BaseFetcher]:
        """
        Get a fetcher by name.
        
        Args:
            name: Name of the fetcher
            
        Returns:
            The fetcher or None if not found
        """
        return self._fetcher_map.get(name)
    
    def get_fetchers_for_category(self, category: ToolCategory) -> List[BaseFetcher]:
        """
        Get all fetchers that support a specific category.
        
        Args:
            category: The tool category
            
        Returns:
            List of fetchers supporting the category
        """
        return self._category_map.get(category, []).copy()
    
    def get_all_fetchers(self) -> List[BaseFetcher]:
        """
        Get all registered fetchers.
        
        Returns:
            List of all fetchers (sorted by priority)
        """
        return self._fetchers.copy()
    
    def get_available_fetchers(self, tool_name: str) -> List[BaseFetcher]:
        """
        Get all fetchers that can handle a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of fetchers that can handle the tool
        """
        available = []
        for fetcher in self._fetchers:
            if fetcher.can_fetch(tool_name):
                available.append(fetcher)
        return available
    
    def fetch_metadata(self, tool_name: str, 
                      category: Optional[ToolCategory] = None,
                      max_fetchers: Optional[int] = None) -> UnifiedMetadata:
        """
        Fetch metadata for a tool using available fetchers.
        
        Args:
            tool_name: Name of the tool to fetch metadata for
            category: Optional tool category to limit fetchers
            max_fetchers: Maximum number of fetchers to try
            
        Returns:
            UnifiedMetadata object with combined results
        """
        start_time = time.time()
        
        # Determine which fetchers to use
        if category:
            fetchers = self.get_fetchers_for_category(category)
        else:
            fetchers = self.get_available_fetchers(tool_name)
        
        # Limit number of fetchers if specified
        if max_fetchers:
            fetchers = fetchers[:max_fetchers]
        
        if not fetchers:
            logger.warning(f"No fetchers available for tool: {tool_name}")
            return self._create_empty_metadata(tool_name, category)
        
        logger.info(f"Using {len(fetchers)} fetchers for {tool_name}: "
                   f"{[f.name for f in fetchers]}")
        
        # Try fetchers in priority order
        best_metadata = None
        successful_fetchers = []
        failed_fetchers = []
        
        for fetcher in fetchers:
            try:
                logger.debug(f"Trying {fetcher.name} for {tool_name}")
                
                metadata = fetcher.fetch_with_timing(tool_name)
                
                if metadata and fetcher.validate_metadata(metadata):
                    successful_fetchers.append(fetcher.name)
                    
                    if best_metadata is None:
                        best_metadata = metadata
                    else:
                        # Merge with existing metadata
                        best_metadata = self._merge_metadata(best_metadata, metadata)
                        
                    logger.info(f"{fetcher.name} successfully fetched metadata for {tool_name}")
                    
                    # If we have complete metadata, we can stop early
                    if best_metadata.is_complete():
                        logger.info(f"Complete metadata obtained for {tool_name}, stopping early")
                        break
                        
                else:
                    logger.debug(f"{fetcher.name} returned invalid metadata for {tool_name}")
                    
            except Exception as e:
                failed_fetchers.append(fetcher.name)
                logger.warning(f"{fetcher.name} failed to fetch {tool_name}: {e}")
        
        # If no fetcher succeeded, create empty metadata
        if best_metadata is None:
            logger.warning(f"All fetchers failed for {tool_name}")
            best_metadata = self._create_empty_metadata(tool_name, category)
        
        # Add registry information
        end_time = time.time()
        best_metadata.fetch_duration = end_time - start_time
        best_metadata.raw_data['registry'] = {
            'successful_fetchers': successful_fetchers,
            'failed_fetchers': failed_fetchers,
            'total_fetchers_tried': len(fetchers)
        }
        
        logger.info(f"Registry completed fetch for {tool_name} in {best_metadata.fetch_duration:.2f}s "
                   f"(successful: {len(successful_fetchers)}, failed: {len(failed_fetchers)})")
        
        return best_metadata
    
    def _create_empty_metadata(self, tool_name: str, 
                              category: Optional[ToolCategory] = None) -> UnifiedMetadata:
        """Create empty metadata for a tool."""
        from .schema import UnifiedMetadata, ToolCategory
        
        return UnifiedMetadata(
            name=tool_name,
            category=category or ToolCategory.GENERIC,
            source_priority="fallback"
        )
    
    def _merge_metadata(self, primary: UnifiedMetadata, 
                       secondary: UnifiedMetadata) -> UnifiedMetadata:
        """
        Merge two metadata objects, with primary taking precedence.
        
        Args:
            primary: Primary metadata object
            secondary: Secondary metadata object to merge
            
        Returns:
            Merged metadata object
        """
        # Merge basic fields (primary takes precedence)
        if not primary.description and secondary.description:
            primary.description = secondary.description
        
        if not primary.version and secondary.version:
            primary.version = secondary.version
        
        if not primary.latest_version and secondary.latest_version:
            primary.latest_version = secondary.latest_version
        
        # Merge links (avoid duplicates)
        existing_urls = {link.url for link in primary.links}
        for link in secondary.links:
            if link.url not in existing_urls:
                primary.links.append(link)
                existing_urls.add(link.url)
        
        # Merge installation methods (avoid duplicates)
        existing_methods = {im.method for im in primary.installation_methods}
        for im in secondary.installation_methods:
            if im.method not in existing_methods:
                primary.installation_methods.append(im)
                existing_methods.add(im.method)
        
        # Merge dependencies
        for version, deps in secondary.dependencies.items():
            if version not in primary.dependencies:
                primary.dependencies[version] = deps
            else:
                # Merge dependency lists
                existing_deps = set(primary.dependencies[version])
                primary.dependencies[version] = list(existing_deps | set(deps))
        
        # Merge category fields
        for key, value in secondary.category_fields.items():
            if key not in primary.category_fields:
                primary.category_fields[key] = value
        
        # Merge sources
        primary.sources.extend(secondary.sources)
        primary.sources = list(set(primary.sources))  # Remove duplicates
        
        # Merge raw data
        primary.raw_data.update(secondary.raw_data)
        
        return primary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the registry.
        
        Returns:
            Dictionary with registry statistics
        """
        stats = {
            'total_fetchers': len(self._fetchers),
            'fetcher_names': list(self._fetcher_map.keys()),
            'categories': {}
        }
        
        for category, fetchers in self._category_map.items():
            stats['categories'][category.value] = {
                'count': len(fetchers),
                'fetchers': [f.name for f in fetchers]
            }
        
        return stats
    
    def __str__(self) -> str:
        return f"FetcherRegistry(fetchers={len(self._fetchers)})"
    
    def __repr__(self) -> str:
        return f"FetcherRegistry(config={self.config}, fetchers={len(self._fetchers)})" 