#!/usr/bin/env python3
"""
Comprehensive test script for all 18 tools to ensure detailed information.
Tests the enhanced MultiSearchFetcher and ensures all tools get comprehensive data.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli.fetcher import MetadataFetcher

def test_all_tools_comprehensive():
    """Test all 18 tools to ensure comprehensive data."""
    
    print("Testing all 18 tools for comprehensive data...")
    print("=" * 60)
    
    # All 18 tools from the classification
    all_tools = [
        "python",
        "pytorch", 
        "tensorflow",
        "anaconda",
        "pandas",
        "jupyterlab",
        "jupyternotebook",
        "r",
        "blender",
        "gimp",
        "elgato_stream_deck",
        "comfyui",
        "visual_studio_code",
        "git_version_control",
        "pycharm",
        "github_desktop",
        "langchain",
        "ollama",
        "hugging_face_transformers"
    ]
    
    # Initialize the fetcher
    fetcher = MetadataFetcher()
    fetcher.setup_registry(output_format="json", output_directory="outputs")
    
    results = {}
    successful = 0
    failed = 0
    
    for i, tool in enumerate(all_tools, 1):
        print(f"\n[{i}/{len(all_tools)}] Testing: {tool}")
        print("-" * 40)
        
        try:
            # Fetch metadata
            metadata = fetcher.fetch_tool_metadata(tool)
            
            if metadata:
                # Check data quality
                data_quality = analyze_data_quality(metadata, tool)
                results[tool] = data_quality
                
                if data_quality['is_comprehensive']:
                    successful += 1
                    print(f"✓ SUCCESS: {tool} - Comprehensive data")
                else:
                    failed += 1
                    print(f"⚠ PARTIAL: {tool} - Missing data")
                    print(f"  Missing fields: {data_quality['missing_fields']}")
                
                print(f"  Description length: {len(metadata.description or '')}")
                print(f"  Features count: {len(metadata.get_field('key_features') or [])}")
                print(f"  Installation steps: {len(metadata.get_field('installation_setup') or [])}")
                print(f"  Links count: {len(metadata.links)}")
                
            else:
                failed += 1
                results[tool] = {'error': 'No metadata found'}
                print(f"✗ FAILED: {tool} - No metadata found")
                
        except Exception as e:
            failed += 1
            results[tool] = {'error': str(e)}
            print(f"✗ ERROR: {tool} - {str(e)}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"testresults/comprehensive_test_{timestamp}.json"
    
    os.makedirs("testresults", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY:")
    print(f"Total tools tested: {len(all_tools)}")
    print(f"Successful (comprehensive): {successful}")
    print(f"Failed/Partial: {failed}")
    print(f"Success rate: {(successful/len(all_tools)*100):.1f}%")
    print(f"Results saved to: {output_file}")
    
    # Show tools that need improvement
    if failed > 0:
        print("\nTools needing improvement:")
        for tool, result in results.items():
            if 'error' in result or not result.get('is_comprehensive', False):
                print(f"  - {tool}: {result.get('error', 'Missing fields: ' + ', '.join(result.get('missing_fields', [])))}")

def analyze_data_quality(metadata, tool_name):
    """Analyze the quality of metadata for a tool."""
    
    # Required fields for comprehensive data
    required_fields = {
        'basic_info': ['tool_name', 'overview_description', 'key_features', 'use_cases', 'supported_platforms'],
        'technical_specs': ['dependencies', 'system_requirements', 'supported_languages', 'supported_file_formats'],
        'setup_info': ['installation_setup', 'configuration_guide', 'quick_start_tutorial'],
        'documentation': ['official_documentation', 'tutorials_examples', 'community_tutorials'],
        'community': ['community_support', 'forums_channels', 'ecosystem_packages'],
        'legal_versioning': ['licensing', 'latest_version', 'release_date'],
        'references': ['official_website', 'github_repository', 'documentation_links']
    }
    
    # Check if metadata has comprehensive data
    missing_fields = []
    has_description = bool(metadata.description and len(metadata.description) > 50)
    has_features = bool(metadata.get_field('key_features') and len(metadata.get_field('key_features')) > 0)
    has_installation = bool(metadata.get_field('installation_setup') and len(metadata.get_field('installation_setup')) > 0)
    has_links = len(metadata.links) >= 5
    
    # Check for missing essential data
    if not has_description:
        missing_fields.append('description')
    if not has_features:
        missing_fields.append('key_features')
    if not has_installation:
        missing_fields.append('installation_setup')
    if not has_links:
        missing_fields.append('links')
    
    # Check if the description is generic
    is_generic = False
    if metadata.description:
        generic_phrases = [
            f"{tool_name} is a software tool used in development",
            f"{tool_name} is a software tool",
            "software tool used in development"
        ]
        is_generic = any(phrase.lower() in metadata.description.lower() for phrase in generic_phrases)
    
    is_comprehensive = (
        has_description and 
        has_features and 
        has_installation and 
        has_links and 
        not is_generic and
        len(missing_fields) == 0
    )
    
    return {
        'is_comprehensive': is_comprehensive,
        'has_description': has_description,
        'has_features': has_features,
        'has_installation': has_installation,
        'has_links': has_links,
        'is_generic': is_generic,
        'missing_fields': missing_fields,
        'description_length': len(metadata.description or ''),
        'features_count': len(metadata.get_field('key_features') or []),
        'installation_count': len(metadata.get_field('installation_setup') or []),
        'links_count': len(metadata.links),
        'sources': metadata.sources
    }

if __name__ == "__main__":
    test_all_tools_comprehensive() 