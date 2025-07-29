"""
Fetchers package for MetadataFetcher.

This package contains all the fetcher implementations that can retrieve
metadata from various sources like PyPI, GitHub, DockerHub, and documentation sites.
"""

from .pypi import PyPIFetcher
from .github import GitHubFetcher
from .docker import DockerHubFetcher
from .docs import DocsFetcher
from .google_cse import GoogleCSEFetcher
from .duckduckgo import DuckDuckGoFetcher
from .bing_search import BingSearchFetcher
from .yandex_search import YandexSearchFetcher
from .main_fetcher import MainFetcher
from .multi_search import MultiSearchFetcher

__all__ = [
    'PyPIFetcher',
    'GitHubFetcher', 
    'DockerHubFetcher',
    'DocsFetcher',
    'GoogleCSEFetcher',
    'DuckDuckGoFetcher',
    'BingSearchFetcher',
    'YandexSearchFetcher',
    'MainFetcher',
    'MultiSearchFetcher'
] 