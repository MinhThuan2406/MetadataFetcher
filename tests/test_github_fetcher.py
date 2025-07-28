import pytest
# DEPRECATED: This test uses old modules that no longer exist
# from metadata.fetchers.pypi_fetcher import fetch_pypi_metadata
# from metadata.fetchers.github_fetcher import enrich_with_github_data

def test_enrich_with_github_data():
    metadata = fetch_pypi_metadata("requests")
    if metadata and metadata.github_url:
        enriched = enrich_with_github_data(metadata)
        # README or requirements may or may not exist, but should not error
        assert hasattr(enriched, "readme_content")
        assert hasattr(enriched, "requirements") 