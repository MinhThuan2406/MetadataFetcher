import pytest
# DEPRECATED: This test uses old modules that no longer exist
# from metadata.fetchers.pypi_fetcher import fetch_pypi_metadata

def test_fetch_pypi_metadata_basic():
    metadata = fetch_pypi_metadata("requests")
    assert metadata is not None
    assert metadata.name == "requests"
    assert metadata.latest_version is not None
    assert isinstance(metadata.popular_versions, list)
    assert isinstance(metadata.dependencies, dict)
    assert metadata.installation.pip == "pip install requests" 