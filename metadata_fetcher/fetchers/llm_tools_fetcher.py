import json
from metadata_fetcher.fetchers.generic_fetcher import fetch_generic_tool_metadata, organize_metadata_for_output
from metadata_fetcher.fetchers.pypi_fetcher import fetch_pypi_metadata
from typing import Dict

TECHNICAL_USE_CASE = "Large Language Models (LLM) Tools"

def fetch_llm_tools_metadata(tool_name: str) -> Dict:
    """Fetch metadata for an LLM tool, using PyPI, generic fetcher, and fallbacks as needed."""
    # Try PyPI fetch first
    metadata = fetch_pypi_metadata(tool_name)
    if metadata is None or getattr(metadata, 'source', None) != 'pypi':
        metadata = fetch_generic_tool_metadata(tool_name)
    if metadata is None:
        return {"Name": tool_name, "status": "not found or manual review needed"}
    return organize_metadata_for_output(metadata, TECHNICAL_USE_CASE) 