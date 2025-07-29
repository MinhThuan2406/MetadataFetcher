#!/usr/bin/env python3
"""
Integration test for MultiSearchFetcher with the main system.
Tests that the new fetcher works properly with the registry and other fetchers.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli.fetcher import MetadataFetcher
from metadata.core import FetcherRegistry, FetcherConfig
from metadata.core.fetchers import MultiSearchFetcher

def test_integration():
    """Test the MultiSearchFetcher integration with the main system."""
    
    print("Testing MultiSearchFetcher Integration...")
    print("=" * 60)
    
    # Test 1: Registry Integration
    print("\n1. Testing Registry Integration")
    print("-" * 30)
    
    try:
        config = FetcherConfig()
        registry = FetcherRegistry(config)
        
        # Register MultiSearchFetcher
        multi_search = MultiSearchFetcher(config)
        registry.register(multi_search)
        
        # Check if it's registered
        all_fetchers = registry.get_all_fetchers()
        multi_search_found = any(f.name == "MultiSearchFetcher" for f in all_fetchers)
        
        if multi_search_found:
            print("✓ MultiSearchFetcher successfully registered in registry")
        else:
            print("✗ MultiSearchFetcher not found in registry")
            return False
            
    except Exception as e:
        print(f"✗ Registry integration failed: {str(e)}")
        return False
    
    # Test 2: Direct Fetcher Test
    print("\n2. Testing Direct Fetcher")
    print("-" * 30)
    
    try:
        config = FetcherConfig()
        fetcher = MultiSearchFetcher(config)
        
        # Test with a simple tool
        test_tool = "pandas"
        metadata = fetcher.fetch(test_tool)
        
        if metadata:
            print(f"✓ Successfully fetched metadata for '{test_tool}'")
            print(f"  Name: {metadata.name}")
            print(f"  Category: {metadata.category.value}")
            print(f"  Description length: {len(metadata.description) if metadata.description else 0}")
            print(f"  Sources: {metadata.sources}")
            print(f"  Raw data keys: {list(metadata.raw_data.keys())}")
        else:
            print(f"✗ Failed to fetch metadata for '{test_tool}'")
            return False
            
    except Exception as e:
        print(f"✗ Direct fetcher test failed: {str(e)}")
        return False
    
    # Test 3: Main System Integration
    print("\n3. Testing Main System Integration")
    print("-" * 30)
    
    try:
        # Create MetadataFetcher (which sets up the registry)
        main_fetcher = MetadataFetcher()
        main_fetcher.setup_registry()
        
        # Check if MultiSearchFetcher is in the registry
        registry = main_fetcher.registry
        all_fetchers = registry.get_all_fetchers()
        multi_search_found = any(f.name == "MultiSearchFetcher" for f in all_fetchers)
        
        if multi_search_found:
            print("✓ MultiSearchFetcher found in main system registry")
            
            # Get the MultiSearchFetcher instance
            multi_search = registry.get_fetcher("MultiSearchFetcher")
            if multi_search:
                print(f"  Priority: {multi_search.get_priority()}")
                print(f"  Supported categories: {[c.value for c in multi_search.get_supported_categories()]}")
            else:
                print("✗ Could not retrieve MultiSearchFetcher from registry")
                return False
        else:
            print("✗ MultiSearchFetcher not found in main system registry")
            return False
            
    except Exception as e:
        print(f"✗ Main system integration failed: {str(e)}")
        return False
    
    # Test 4: End-to-End Test
    print("\n4. Testing End-to-End Functionality")
    print("-" * 30)
    
    try:
        # Test with a tool that should work well with search engines
        test_tools = ["tensorflow", "git", "docker"]
        results = {}
        
        for tool in test_tools:
            print(f"\n  Testing: {tool}")
            metadata = fetcher.fetch(tool)
            
            if metadata:
                results[tool] = {
                    'success': True,
                    'category': metadata.category.value,
                    'description_length': len(metadata.description) if metadata.description else 0,
                    'sources': metadata.sources,
                    'urls_count': len(metadata.raw_data.get('urls', [])),
                    'search_sources_count': len(metadata.raw_data.get('search_sources', []))
                }
                print(f"    ✓ Success: {metadata.category.value} ({results[tool]['urls_count']} URLs)")
            else:
                results[tool] = {'success': False, 'error': 'No metadata returned'}
                print(f"    ✗ Failed: No metadata returned")
        
        # Summary
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        print(f"\n  Summary: {successful}/{total} successful")
        
        if successful > 0:
            print("✓ End-to-end test passed")
        else:
            print("✗ End-to-end test failed")
            return False
            
    except Exception as e:
        print(f"✗ End-to-end test failed: {str(e)}")
        return False
    
    # Test 5: Performance Test
    print("\n5. Testing Performance")
    print("-" * 30)
    
    try:
        import time
        
        start_time = time.time()
        metadata = fetcher.fetch("python")
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"  Fetch time: {duration:.2f} seconds")
        
        if duration < 30:  # Should complete within 30 seconds
            print("✓ Performance test passed (reasonable fetch time)")
        else:
            print("✗ Performance test failed (fetch time too long)")
            return False
            
    except Exception as e:
        print(f"✗ Performance test failed: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! MultiSearchFetcher is successfully integrated.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 