import pytest
# DEPRECATED: This test uses old modules that no longer exist
# from metadata.google_search import google_search

def test_google_search_milvus():
    url = google_search("milvus official site")
    assert url is not None
    assert url.startswith("http") 