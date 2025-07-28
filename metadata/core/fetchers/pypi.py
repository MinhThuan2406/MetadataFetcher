"""
PyPI fetcher for the unified MetadataFetcher architecture.
"""

from typing import Optional, List
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
import logging

logger = logging.getLogger(__name__)

class PyPIFetcher(BaseFetcher):
    """
    Fetches metadata for Python packages from PyPI.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "PyPIFetcher"
    
    def can_fetch(self, tool_name: str) -> bool:
        # Heuristic: PyPI fetcher is for Python packages (not for generic tools)
        # You may want to improve this with a real check
        return tool_name.lower() not in [
            'git', 'blender', 'gimp', 'comfyui', 'elgatostreamdeck', 'githubdesktop', 'pycharm', 'visualstudiocode', 'r'
        ]
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata from PyPI."""
        try:
            # Check cache first
            cached_metadata = self._get_cached_metadata(tool_name)
            if cached_metadata:
                logger.info(f"Using cached metadata for {tool_name}")
                return cached_metadata
            
            # Make API request
            url = f"https://pypi.org/pypi/{tool_name}/json"
            response = requests.get(url, timeout=self.config.timeout)
            
            if response.status_code == 404:
                logger.warning(f"PyPI: {tool_name} not found (status 404)")
                return None
            
            if response.status_code != 200:
                logger.warning(f"PyPI: {tool_name} request failed (status {response.status_code})")
                return None
            
            data = response.json()
            
            # Build metadata
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=data.get('info', {}).get('name', tool_name),
                description=data.get('info', {}).get('summary', ''),
                version=data.get('info', {}).get('version', ''),
                latest_version=data.get('info', {}).get('version', ''),
                category=ToolCategory.AI_ML,  # Default for Python packages
                homepage=data.get('info', {}).get('home_page'),
                documentation=data.get('info', {}).get('docs_url'),
                repository=data.get('info', {}).get('project_urls', {}).get('Repository'),
                license=data.get('info', {}).get('license'),
                author=data.get('info', {}).get('author'),
                maintainer=data.get('info', {}).get('maintainer'),
                source_priority="online"
            )
            
            # Add installation method
            metadata.add_installation_method(
                method="pip",
                command=f"pip install {tool_name}",
                description=f"Install {tool_name} using pip"
            )
            
            # Add dependencies
            if 'requires_dist' in data.get('info', {}):
                metadata.dependencies['latest'] = data['info']['requires_dist']
            
            # Cache the result
            self._cache_metadata(tool_name, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error fetching {tool_name} from PyPI: {e}")
            return None
    
    def get_priority(self) -> int:
        return 5  # High priority for PyPI
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.AI_ML, ToolCategory.DATA_SCIENCE, ToolCategory.GENERIC] 