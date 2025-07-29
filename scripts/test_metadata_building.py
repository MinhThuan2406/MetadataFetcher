#!/usr/bin/env python3
"""
Test script to debug metadata building process.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metadata.core.fetchers.multi_search import MultiSearchFetcher
from metadata.core.config import FetcherConfig

def test_metadata_building():
    """Test the metadata building process."""
    
    print("Testing metadata building process...")
    print("=" * 60)
    
    # Initialize the fetcher
    config = FetcherConfig()
    fetcher = MultiSearchFetcher(config)
    
    # Test with a tool that has language issues
    tool_name = "anaconda"
    
    print(f"Testing metadata building for: {tool_name}")
    print("-" * 40)
    
    try:
        # Test fallback description
        fallback_desc = fetcher._get_fallback_description(tool_name)
        print(f"Fallback description: {fallback_desc}")
        
        # Create a mock result with Chinese content
        mock_results = [
            {
                'title': 'Anaconda Chinese Guide',
                'url': 'https://www.zhihu.com/question/426285725',
                'snippet': '如果提示地址不正确，可以尝试打开anaconda坐在的文件夹，找到anaconda3\\bin，直接拖到终端内，可以看到完整的路径，替换上面""内的内容即可',
                'source': 'google',
                'domain': 'zhihu.com'
            }
        ]
        
        # Test metadata building
        metadata = fetcher._build_metadata_from_results(tool_name, mock_results)
        
        print(f"Final description: {metadata.description}")
        print(f"Description length: {len(metadata.description)}")
        print(f"Contains Chinese: {'如果' in metadata.description}")
        print(f"Contains fallback content: {'Anaconda is a distribution' in metadata.description}")
        
        # Test field population
        features = metadata.get_field('key_features')
        installation = metadata.get_field('installation_setup')
        
        print(f"Features count: {len(features) if features else 0}")
        print(f"Installation steps: {len(installation) if installation else 0}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metadata_building() 