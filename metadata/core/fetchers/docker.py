"""
DockerHub fetcher for the unified MetadataFetcher architecture.
"""

from typing import Optional, List
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
import logging

logger = logging.getLogger(__name__)

class DockerHubFetcher(BaseFetcher):
    """
    Fetches metadata for tools from DockerHub.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "DockerHubFetcher"
        self.api_url = "https://hub.docker.com/api/content/v1/products/search"
    
    def can_fetch(self, tool_name: str) -> bool:
        # Heuristic: DockerHub fetcher is for container-related tools
        # You may want to improve this with better detection
        docker_keywords = ['docker', 'container', 'image', 'kubernetes', 'k8s']
        return any(keyword in tool_name.lower() for keyword in docker_keywords) or tool_name.lower() in [
            'nginx', 'redis', 'postgres', 'mysql', 'mongo', 'elasticsearch', 'rabbitmq'
        ]
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata for a tool from DockerHub."""
        try:
            # Search for Docker images
            params = {
                "q": tool_name,
                "type": "image",
                "page_size": 1
            }
            headers = {
                "Accept": "application/json"
            }
            resp = requests.get(self.api_url, params=params, headers=headers, timeout=self.config.timeout)
            if resp.status_code != 200:
                logger.warning(f"DockerHub: search failed for {tool_name} (status {resp.status_code})")
                return None
            data = resp.json()
            if not data.get("summaries"):
                logger.warning(f"DockerHub: no images found for {tool_name}")
                return None
            image = data["summaries"][0]
            # Build metadata
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=image.get("name", tool_name),
                description=image.get("short_description"),
                category=ToolCategory.DEVELOPER_TOOLS,  # Default for container tools
                source_priority="online"
            )
            # Add Docker installation method
            metadata.add_installation_method(
                method="docker",
                command=f"docker pull {image.get('name', tool_name)}",
                description=f"Pull {tool_name} Docker image"
            )
            # Add Docker run command
            metadata.add_installation_method(
                method="docker_run",
                command=f"docker run {image.get('name', tool_name)}",
                description=f"Run {tool_name} Docker container"
            )
            # Add category fields
            metadata.category_fields["docker_stars"] = image.get("star_count", 0)
            metadata.category_fields["docker_pulls"] = image.get("pull_count", 0)
            metadata.category_fields["docker_official"] = image.get("is_official", False)
            metadata.category_fields["docker_automated"] = image.get("is_automated", False)
            metadata.category_fields["docker_tags"] = image.get("tag_count", 0)
            # Add repository link
            if image.get("name"):
                repo_url = f"https://hub.docker.com/r/{image['name']}"
                metadata.add_link(
                    url=repo_url,
                    title="DockerHub Repository",
                    link_type="repository"
                )
            return metadata
        except Exception as e:
            logger.warning(f"Failed to fetch {tool_name} from DockerHub: {e}")
            return None
    
    def get_priority(self) -> int:
        return 30  # Lower priority than PyPI and GitHub
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.DEVELOPER_TOOLS, ToolCategory.GENERIC] 