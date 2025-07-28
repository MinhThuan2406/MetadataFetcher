#!/usr/bin/env python3
"""
Test Comprehensive Fetcher
Tests the comprehensive metadata fetcher to ensure it generates the correct format
"""

import sys
import json
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# DEPRECATED: This test uses old modules that no longer exist
# from metadata.fetchers.comprehensive_fetcher import fetch_comprehensive_metadata, save_comprehensive_metadata_json

def test_comprehensive_fetcher():
    """Test the comprehensive fetcher with a few sample tools."""
    
    print("Testing Comprehensive Metadata Fetcher")
    print("=" * 50)
    
    # Test tools from different categories
    test_tools = [
        ('python', 'ai_ml'),
        ('blender', 'creative_media'),
        ('pandas', 'data_science'),
        ('git', 'developer_tools'),
        ('huggingfacetransformers', 'llm_tools')
    ]
    
    results = []
    
    for tool_name, expected_category in test_tools:
        print(f"\nTesting {tool_name} (expected category: {expected_category})")
        
        try:
            # Fetch comprehensive metadata
            metadata = fetch_comprehensive_metadata(tool_name)
            
            # Save to JSON
            output_file = save_comprehensive_metadata_json(metadata, tool_name, expected_category)
            
            # Verify the output file exists and has content
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Check that it has the expected structure
                required_fields = ['tool_name', 'overview_description']
                missing_fields = [field for field in required_fields if field not in json_data]
                
                if missing_fields:
                    print(f"  ✗ Missing required fields: {missing_fields}")
                else:
                    print(f"  ✓ Successfully generated metadata for {tool_name}")
                    print(f"    Output file: {output_file}")
                    print(f"    Tool name: {json_data.get('tool_name', 'N/A')}")
                    print(f"    Description length: {len(json_data.get('overview_description', ''))} characters")
                    
                    # Check category-specific fields
                    if expected_category == 'ai_ml' and 'primary_use_cases' in json_data:
                        print(f"    Primary use cases: {len(json_data['primary_use_cases'])} items")
                    elif expected_category == 'creative_media' and 'main_functions' in json_data:
                        print(f"    Main functions: {len(json_data['main_functions'])} items")
                    elif expected_category == 'data_science' and 'typical_applications' in json_data:
                        print(f"    Typical applications: {len(json_data['typical_applications'])} items")
                    elif expected_category == 'developer_tools' and 'development_features' in json_data:
                        print(f"    Development features: {len(json_data['development_features'])} items")
                    elif expected_category == 'llm_tools' and 'model_support' in json_data:
                        print(f"    Model support: {len(json_data['model_support'])} items")
                    
                    results.append((tool_name, True, output_file))
            else:
                print(f"  ✗ Output file not created: {output_file}")
                results.append((tool_name, False, None))
                
        except Exception as e:
            print(f"  ✗ Error processing {tool_name}: {e}")
            results.append((tool_name, False, None))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Successfully processed: {successful}/{total} tools")
    
    for tool_name, success, output_file in results:
        status = "✓" if success else "✗"
        print(f"  {status} {tool_name}")
        if success and output_file:
            print(f"    Output: {output_file}")
    
    if successful == total:
        print("\n🎉 All tests passed! The comprehensive fetcher is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - successful} tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = test_comprehensive_fetcher()
    sys.exit(exit_code) 