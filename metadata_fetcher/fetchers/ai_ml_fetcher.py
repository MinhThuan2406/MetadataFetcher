import json
from metadata_fetcher.fetchers.generic_fetcher import fetch_generic_tool_metadata, organize_metadata_for_output
from metadata_fetcher import fetch_package_metadata
from typing import Dict

TECHNICAL_USE_CASE = "AI/ML Development Tools"

def fetch_ai_ml_metadata(tool_name: str) -> Dict:
    """Fetch metadata for an AI/ML tool, using PyPI, generic fetcher, and fallbacks as needed."""
    # Try PyPI fetch first
    metadata = fetch_package_metadata(tool_name)
    if metadata is None or getattr(metadata, 'source', None) != 'pypi':
        metadata = fetch_generic_tool_metadata(tool_name)
    if metadata is None:
        return {"Name": tool_name, "status": "not found or manual review needed"}
    return organize_metadata_for_output(metadata, TECHNICAL_USE_CASE) 