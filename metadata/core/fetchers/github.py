"""
GitHub fetcher for the unified MetadataFetcher architecture.
"""

from typing import Optional, List
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
import logging

logger = logging.getLogger(__name__)

class GitHubFetcher(BaseFetcher):
    """
    Fetches metadata for tools from GitHub repositories.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "GitHubFetcher"
        self.api_url = "https://api.github.com"
    
    def can_fetch(self, tool_name: str) -> bool:
        # Heuristic: Try to fetch for any tool, but prioritize if 'github' in name or as fallback
        return True
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata for a tool from GitHub."""
        try:
            # Search for the most relevant repository
            search_url = f"{self.api_url}/search/repositories"
            params = {
                "q": tool_name,
                "sort": "stars",
                "order": "desc",
                "per_page": 1
            }
            headers = {}
            if self.config.github_token:
                headers["Authorization"] = f"token {self.config.github_token}"
            resp = requests.get(search_url, params=params, headers=headers, timeout=self.config.timeout)
            if resp.status_code != 200:
                logger.warning(f"GitHub: search failed for {tool_name} (status {resp.status_code})")
                return None
            items = resp.json().get("items", [])
            if not items:
                logger.warning(f"GitHub: no repositories found for {tool_name}")
                return None
            repo = items[0]
            # Fetch README
            readme_url = f"{self.api_url}/repos/{repo['full_name']}/readme"
            readme_resp = requests.get(readme_url, headers=headers, timeout=self.config.timeout)
            readme_content = None
            if readme_resp.status_code == 200:
                readme_json = readme_resp.json()
                import base64
                if 'content' in readme_json:
                    readme_content = base64.b64decode(readme_json['content']).decode('utf-8', errors='replace')
            # Build metadata
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=repo.get("name", tool_name),
                description=repo.get("description"),
                homepage=repo.get("homepage"),
                repository=repo.get("html_url"),
                category=ToolCategory.DEVELOPER_TOOLS,  # Default, can be improved
                readme_content=readme_content,
                source_priority="online"
            )
            # Add stars, forks, etc. as category fields
            metadata.category_fields["github_stars"] = repo.get("stargazers_count")
            metadata.category_fields["github_forks"] = repo.get("forks_count")
            metadata.category_fields["github_language"] = repo.get("language")
            metadata.category_fields["github_license"] = repo.get("license", {}).get("name") if repo.get("license") else None
            metadata.category_fields["github_topics"] = repo.get("topics", [])
            metadata.category_fields["github_full_name"] = repo.get("full_name")
            metadata.category_fields["github_created_at"] = repo.get("created_at")
            metadata.category_fields["github_updated_at"] = repo.get("updated_at")
            # Add repository link
            metadata.add_link(
                url=repo.get("html_url"),
                title="GitHub Repository",
                link_type="repository"
            )
            # Add homepage link if available
            if repo.get("homepage"):
                metadata.add_link(
                    url=repo.get("homepage"),
                    title="Homepage",
                    link_type="homepage"
                )
            return metadata
        except Exception as e:
            logger.warning(f"Failed to fetch {tool_name} from GitHub: {e}")
            return None
    
    def get_priority(self) -> int:
        return 20  # Lower priority than PyPI
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.DEVELOPER_TOOLS, ToolCategory.GENERIC] 