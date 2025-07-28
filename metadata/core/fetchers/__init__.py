"""
Fetchers package for MetadataFetcher.

This package contains all the fetcher implementations that can retrieve
metadata from various sources like PyPI, GitHub, DockerHub, and documentation sites.
"""

from .pypi import PyPIFetcher
from .github import GitHubFetcher
from .docker import DockerHubFetcher
from .docs import DocsFetcher

__all__ = [
    'PyPIFetcher',
    'GitHubFetcher', 
    'DockerHubFetcher',
    'DocsFetcher'
] 