"""
Documentation site fetcher for the unified MetadataFetcher architecture.
"""

from typing import Optional, List
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

class DocsFetcher(BaseFetcher):
    """
    Fetches metadata by scraping official documentation sites.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "DocsFetcher"
    
    def can_fetch(self, tool_name: str) -> bool:
        # This fetcher can handle any tool as a fallback
        return True
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata by scraping documentation sites."""
        try:
            # Try to find documentation URL
            doc_url = self._find_documentation_url(tool_name)
            if not doc_url:
                return None
            
            # Fetch and parse the documentation page
            response = requests.get(doc_url, timeout=self.config.timeout)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metadata
            title = self._extract_title(soup, tool_name)
            description = self._extract_description(soup)
            installation_methods = self._extract_installation_methods(soup, tool_name)
            links = self._extract_links(soup, doc_url)
            
            # Build metadata
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=title,
                description=description,
                documentation=doc_url,
                category=ToolCategory.GENERIC,
                source_priority="online"
            )
            
            # Add installation methods
            for method in installation_methods:
                metadata.add_installation_method(**method)
            
            # Add links
            for link in links:
                metadata.add_link(**link)
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to fetch {tool_name} from documentation: {e}")
            return None
    
    def _find_documentation_url(self, tool_name: str) -> Optional[str]:
        """Find the documentation URL for a tool."""
        # Common documentation URL patterns
        patterns = [
            f"https://docs.{tool_name}.org",
            f"https://{tool_name}.readthedocs.io",
            f"https://{tool_name}.io/docs",
            f"https://docs.{tool_name}.io",
            f"https://{tool_name}.com/docs",
            f"https://docs.{tool_name}.com",
            f"https://{tool_name}.github.io",
            f"https://{tool_name}.dev",
            f"https://docs.{tool_name}.dev"
        ]
        
        for pattern in patterns:
            try:
                response = requests.head(pattern, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return pattern
            except:
                continue
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup, tool_name: str) -> str:
        """Extract the page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return tool_name.title()
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            if len(text) > 50:  # Only if it's substantial
                return text[:200] + "..." if len(text) > 200 else text
        
        return None
    
    def _extract_installation_methods(self, soup: BeautifulSoup, tool_name: str) -> List[dict]:
        """Extract installation methods from documentation."""
        methods = []
        
        # Look for installation sections
        installation_sections = soup.find_all(['h1', 'h2', 'h3', 'h4'], 
                                           text=re.compile(r'install|setup|getting started', re.I))
        
        for section in installation_sections:
            # Look for code blocks in this section
            code_blocks = section.find_next_siblings(['pre', 'code'])
            for block in code_blocks:
                code_text = block.get_text().strip()
                if code_text and len(code_text) < 200:  # Reasonable length
                    methods.append({
                        'method': 'docs',
                        'command': code_text,
                        'description': f"Installation method from {tool_name} documentation"
                    })
        
        return methods
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[dict]:
        """Extract relevant links from documentation."""
        links = []
        
        # Look for common documentation links
        link_patterns = [
            'api', 'reference', 'tutorial', 'guide', 'examples', 'download',
            'installation', 'setup', 'quickstart', 'getting-started'
        ]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().lower()
            
            # Check if it's a relevant link
            if any(pattern in href.lower() or pattern in text for pattern in link_patterns):
                # Make relative URLs absolute
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    continue
                
                links.append({
                    'url': href,
                    'title': link.get_text().strip(),
                    'link_type': 'documentation'
                })
        
        return links
    
    def get_priority(self) -> int:
        return 40  # Lower priority than PyPI, GitHub, and DockerHub
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.GENERIC] 