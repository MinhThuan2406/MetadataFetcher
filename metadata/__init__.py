from .core.schema import UnifiedMetadata, ToolCategory
from .core import FetcherRegistry, FetcherConfig
from .core.fetchers import PyPIFetcher, GitHubFetcher, DockerHubFetcher, DocsFetcher

def fetch_package_metadata(app_name: str) -> UnifiedMetadata | None:
    """
    Orchestrates fetching metadata for a package using the unified fetcher system.
    Returns a unified UnifiedMetadata object or None if not found.
    """
    config = FetcherConfig()
    registry = FetcherRegistry(config)
    registry.register_class(PyPIFetcher)
    registry.register_class(GitHubFetcher)
    return registry.fetch_metadata(app_name)

def fetch_comprehensive_tool_metadata(tool_name: str) -> UnifiedMetadata:
    """
    Fetch comprehensive metadata for a tool using all available fetchers.
    Returns a UnifiedMetadata object with detailed information.
    """
    config = FetcherConfig()
    registry = FetcherRegistry(config)
    registry.register_class(PyPIFetcher)
    registry.register_class(GitHubFetcher)
    registry.register_class(DockerHubFetcher)
    registry.register_class(DocsFetcher)
    return registry.fetch_metadata(tool_name)



