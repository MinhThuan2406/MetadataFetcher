import json
from metadata_fetcher import fetch_package_metadata
from metadata_fetcher.generic_fetcher import fetch_generic_tool_metadata, organize_metadata_for_output

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

def fetch_data_science_metadata(tool_name: str) -> dict:
    tool_key = tool_name.strip().lower()
    fallbacks = TOOL_FALLBACKS.get(tool_key, {})
    # Try PyPI fetch first
    metadata = fetch_package_metadata(tool_name)
    if metadata is None or getattr(metadata, 'source', None) != 'pypi':
        metadata = fetch_generic_tool_metadata(tool_name)
    if metadata is None:
        # If all else fails, return minimal info from fallbacks
        return {
            "General Info": {
                "Name": tool_name,
                "Use Case": TECHNICAL_USE_CASE,
                "Homepage": fallbacks.get('homepage', 'N/A'),
                "Description": 'N/A',
            },
            "Documentation": {
                "Main Documentation": fallbacks.get('documentation', 'N/A'),
                "Top Links": []
            },
            "Installation": {
                "Links": [],
                "Summary": {}
            },
            "Other Links": {
                "All Documentation Links": [],
                "All Installation Links": []
            },
            "Support": fallbacks.get('support', 'N/A')
        }
    # Patch missing fields with fallbacks
    if hasattr(metadata, 'homepage') and (not metadata.homepage or metadata.homepage == 'N/A'):
        metadata.homepage = fallbacks.get('homepage', metadata.homepage)
    if hasattr(metadata, 'documentation') and (not metadata.documentation or metadata.documentation == 'N/A'):
        metadata.documentation = fallbacks.get('documentation', metadata.documentation)
    # Always prefer YAML description and use_case for known tools (enforced override)
    try:
        import yaml
        with open("tool_descriptions.yaml", "r", encoding="utf-8") as f:
            tool_descriptions = yaml.safe_load(f)
        key = tool_name.strip().lower()
        if key in tool_descriptions:
            old_desc = getattr(metadata, 'description', '') if isinstance(getattr(metadata, 'description', ''), str) else ''
            old_use_case = getattr(metadata, 'use_case', '') if isinstance(getattr(metadata, 'use_case', ''), str) else ''
            metadata.description = tool_descriptions[key].get("description", metadata.description)
            metadata.use_case = tool_descriptions[key].get("use_case", metadata.use_case)
            desc_val = metadata.description if isinstance(metadata.description, str) else ''
            use_case_val = metadata.use_case if isinstance(metadata.use_case, str) else ''
            old_desc_val = old_desc if isinstance(old_desc, str) else ''
            old_use_case_val = old_use_case if isinstance(old_use_case, str) else ''
            print(f"[DEBUG] YAML override for '{tool_name}': description set to '{desc_val[:60]}...', use_case set to '{use_case_val}' (was '{old_desc_val[:60]}...', '{old_use_case_val}')")
    except Exception as e:
        print(f"[WARN] Could not load tool_descriptions.yaml: {e}")
    # Patch support into output after organize_metadata_for_output
    output = organize_metadata_for_output(metadata, metadata.use_case or TECHNICAL_USE_CASE)
    if 'Support' not in output:
        output['Support'] = fallbacks.get('support', 'N/A')
    # Debug print for final output
    if output and isinstance(output, dict):
        general_info = output.get('General Info', {}) if isinstance(output.get('General Info', {}), dict) else {}
        desc_out = general_info.get('Description', '') or ''
        use_case_out = general_info.get('Use Case', '') or ''
        print(f"[DEBUG] Final output for '{tool_name}': Description='{desc_out[:60]}...', Use Case='{use_case_out}'")
    else:
        print(f"[DEBUG] Final output for '{tool_name}': Output is None or not a dict")
    return output 