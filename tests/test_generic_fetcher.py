import pytest
# DEPRECATED: This test uses old modules that no longer exist
# from metadata.fetchers.generic_fetcher import fetch_generic_tool_metadata

def test_fetch_generic_tool_metadata_milvus():
    metadata = fetch_generic_tool_metadata("milvus")
    assert metadata is not None
    assert metadata.homepage is not None
    assert metadata.documentation is not None
    assert isinstance(metadata.documentation_links, list)
    assert isinstance(metadata.installation_links, list) 