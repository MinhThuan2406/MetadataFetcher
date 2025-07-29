#!/usr/bin/env python3
"""
Test script for MultiSearchFetcher.
Tests the new multi-search engine fetcher with various tools.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metadata.core.fetchers.multi_search import MultiSearchFetcher
from metadata.core.config import FetcherConfig

def test_multi_search_fetcher():
    """Test the MultiSearchFetcher with various tools."""
    
    print("Testing MultiSearchFetcher...")
    print("=" * 50)
    
    # Initialize the fetcher
    config = FetcherConfig()
    fetcher = MultiSearchFetcher(config)
    
    # Test tools
    test_tools = [
        "python",
        "pandas", 
        "tensorflow",
        "git",
        "docker",
        "vscode"
    ]
    
    results = {}
    
    for tool in test_tools:
        print(f"\nTesting: {tool}")
        print("-" * 30)
        
        try:
            metadata = fetcher.fetch(tool)
            if metadata:
                results[tool] = {
                    'name': metadata.name,
                    'description': metadata.description[:100] + "..." if len(metadata.description) > 100 else metadata.description,
                    'category': metadata.category.value,
                    'urls_count': len(metadata.raw_data.get('urls', [])),
                    'sources_count': len(metadata.raw_data.get('search_sources', [])),
                    'metadata_source': metadata.sources[0] if metadata.sources else 'unknown'
                }
                print(f"✓ Success: {metadata.name}")
                print(f"  Category: {metadata.category.value}")
                print(f"  URLs found: {len(metadata.raw_data.get('urls', []))}")
                print(f"  Sources: {metadata.raw_data.get('search_sources', [])}")
            else:
                results[tool] = {'error': 'No metadata found'}
                print(f"✗ No metadata found for {tool}")
                
        except Exception as e:
            results[tool] = {'error': str(e)}
            print(f"✗ Error: {str(e)}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"testresults/multi_search_test_{timestamp}.json"
    
    os.makedirs("testresults", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    successful = sum(1 for r in results.values() if 'error' not in r)
    total = len(results)
    print(f"Successful: {successful}/{total}")
    
    for tool, result in results.items():
        if 'error' not in result:
            print(f"  ✓ {tool}: {result['category']} ({result['urls_count']} URLs)")
        else:
            print(f"  ✗ {tool}: {result['error']}")

if __name__ == "__main__":
    test_multi_search_fetcher() 