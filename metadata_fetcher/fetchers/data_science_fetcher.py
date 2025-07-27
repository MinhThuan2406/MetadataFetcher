import json
from metadata_fetcher.fetchers.generic_fetcher import fetch_generic_tool_metadata
from metadata_fetcher import fetch_package_metadata
from typing import Optional
import yaml

TECHNICAL_USE_CASE = "Data Science and Analytics Tools"

# Mapping for tool-specific homepages and docs as fallback for Data Science and Analytics Tools
TOOL_FALLBACKS = {
    'pandas': {
        'homepage': 'https://pandas.pydata.org/',
        'documentation': 'https://pandas.pydata.org/docs/',
        'support': 'https://pandas.pydata.org/community/',
    },
    'jupyterlab': {
        'homepage': 'https://jupyter.org/',
        'documentation': 'https://jupyterlab.readthedocs.io/en/stable/',
        'support': 'https://discourse.jupyter.org/c/jupyterlab/11',
    },
    'jupyternotebook': {
        'homepage': 'https://jupyter.org/',
        'documentation': 'https://jupyter-notebook.readthedocs.io/en/stable/',
        'support': 'https://discourse.jupyter.org/c/notebook/12',
    },
    'r': {
        'homepage': 'https://www.r-project.org/',
        'documentation': 'https://cran.r-project.org/manuals.html',
        'support': 'https://cran.r-project.org/web/views/FAQ.html',
    }
}

# Load the YAML field structure for Data Science and Analytics Tools
with open("tool_descriptions.yaml", "r", encoding="utf-8") as f:
    tool_descriptions_yaml = yaml.safe_load(f)
DSA_FIELDS = tool_descriptions_yaml["Data_Science_and_Analytics_Tools"]["fields"]


def fetch_data_science_metadata(tool_name: str) -> dict:
    """Fetch metadata for a data science tool, using PyPI, generic fetcher, and fallbacks as needed. Output strictly follows YAML field structure."""
    tool_key = tool_name.strip().lower()
    fallbacks = TOOL_FALLBACKS.get(tool_key, {})
    # Try PyPI fetch first
    metadata = fetch_package_metadata(tool_name)
    if metadata is None or getattr(metadata, 'source', None) != 'pypi':
        metadata = fetch_generic_tool_metadata(tool_name)
    # Prepare output dict strictly by YAML fields
    output = {}
    for field in DSA_FIELDS:
        value = None
        # Map fields to metadata attributes or fallbacks
        if field == "Tool Name":
            value = getattr(metadata, 'name', None) if metadata else tool_name
        elif field == "Overview / Description":
            value = getattr(metadata, 'description', None) if metadata else 'N/A'
        elif field == "Typical Applications":
            value = getattr(metadata, 'use_case', None) if metadata else TECHNICAL_USE_CASE
        elif field == "Data Formats Supported":
            value = getattr(metadata, 'data_formats_supported', None) if metadata and hasattr(metadata, 'data_formats_supported') else 'N/A'
        elif field == "Visualization Capabilities":
            value = getattr(metadata, 'visualization_capabilities', None) if metadata and hasattr(metadata, 'visualization_capabilities') else 'N/A'
        elif field == "Integration with Other Libraries":
            value = getattr(metadata, 'integration', None) if metadata and hasattr(metadata, 'integration') else 'N/A'
        elif field == "Installation & Setup":
            # Try to summarize installation info
            if metadata and hasattr(metadata, 'installation') and metadata.installation:
                value = str(metadata.installation)
            else:
                value = 'N/A'
        elif field == "Key Features":
            value = getattr(metadata, 'features', None) if metadata and hasattr(metadata, 'features') else 'N/A'
        elif field == "Community & Ecosystem":
            value = fallbacks.get('support', 'N/A')
        elif field == "Documentation & Learning Resources":
            value = getattr(metadata, 'documentation', None) if metadata else fallbacks.get('documentation', 'N/A')
        elif field == "Licensing":
            value = getattr(metadata, 'license', None) if metadata and hasattr(metadata, 'license') else 'N/A'
        elif field == "Latest Version / Release Date":
            value = getattr(metadata, 'version', None) if metadata and hasattr(metadata, 'version') else 'N/A'
        elif field == "Example Use Cases":
            value = getattr(metadata, 'example_use_cases', None) if metadata and hasattr(metadata, 'example_use_cases') else 'N/A'
        elif field == "References (Official Website, Docs, etc.)":
            refs = []
            if metadata:
                if getattr(metadata, 'homepage', None):
                    refs.append(f"Homepage: {metadata.homepage}")
                if getattr(metadata, 'documentation', None):
                    refs.append(f"Documentation: {metadata.documentation}")
            if not refs:
                if fallbacks.get('homepage'):
                    refs.append(f"Homepage: {fallbacks['homepage']}")
                if fallbacks.get('documentation'):
                    refs.append(f"Documentation: {fallbacks['documentation']}")
            value = refs if refs else 'N/A'
        else:
            value = 'N/A'
        output[field] = value
    return output 