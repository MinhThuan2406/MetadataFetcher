#!/usr/bin/env python3
"""
Debug script to test language filtering and fallback data usage.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metadata.core.fetchers.multi_search import MultiSearchFetcher
from metadata.core.config import FetcherConfig

def test_language_filtering():
    """Test the language filtering functionality."""
    
    print("Testing language filtering and fallback data...")
    print("=" * 60)
    
    # Initialize the fetcher
    config = FetcherConfig()
    fetcher = MultiSearchFetcher(config)
    
    # Test tools with known language issues
    test_tools = [
        "anaconda",
        "github_desktop", 
        "pytorch"
    ]
    
    for tool in test_tools:
        print(f"\nTesting: {tool}")
        print("-" * 40)
        
        try:
            # Test the fallback description
            fallback_desc = fetcher._get_fallback_description(tool)
            print(f"Fallback description: {fallback_desc[:100]}...")
            
            # Test content validation
            test_content = [
                "如果提示地址不正确，可以尝试打开anaconda坐在的文件夹",  # Chinese
                "Bonjour, En réponse à popope",  # French
                "PyTorch is an open-source machine learning framework"  # English
            ]
            
            for content in test_content:
                is_valid = fetcher._is_valid_english_content(content)
                print(f"Content: '{content[:50]}...' -> Valid: {is_valid}")
            
            # Test link validation
            test_links = [
                ("https://www.zhihu.com/question/426285725", "mac如何卸载anaconda？ - 知乎"),
                ("https://www.60millions-mag.com/forum/amazon-f143/debit-injustifie-d-amazon-t202997.html", "Débit injustifié d'Amazon"),
                ("https://pytorch.org/docs/", "PyTorch Documentation")
            ]
            
            for url, title in test_links:
                is_valid = fetcher._is_valid_link(url, title)
                print(f"Link: '{title[:30]}...' -> Valid: {is_valid}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_language_filtering() 