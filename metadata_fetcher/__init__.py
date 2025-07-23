from metadata_fetcher.schema import PackageMetadata, InstallationInfo
from metadata_fetcher.pypi_fetcher import fetch_pypi_metadata
from metadata_fetcher.github_fetcher import enrich_with_github_data

def fetch_package_metadata(app_name: str) -> PackageMetadata | None:
    """
    Orchestrates fetching metadata for a PyPI package and enriches it with GitHub data if available.
    Returns a unified PackageMetadata object or None if not found.
    """
    metadata = fetch_pypi_metadata(app_name)
    if metadata is None:
        return None
    if metadata.github_url:
        metadata = enrich_with_github_data(metadata)
    return metadata



