"""
Example usage of the unified MetadataFetcher architecture.

This demonstrates how to use the new refactored system with the
unified metadata schema and fetcher registry.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import metadata
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metadata.core import (
    FetcherRegistry, 
    FetcherConfig, 
    UnifiedMetadata, 
    ToolCategory
)
from metadata.core.base import BaseFetcher
from metadata.core.fetchers import PyPIFetcher, GitHubFetcher
from typing import Optional, List
from metadata.core.basic import save_to_json, save_to_yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ExampleWebFetcher(BaseFetcher):
    """
    Example web scraping fetcher.
    
    This demonstrates a fetcher that scrapes web pages for metadata.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "ExampleWebFetcher"
    
    def can_fetch(self, tool_name: str) -> bool:
        # This fetcher can handle any tool (fallback)
        return True
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        import requests
        from bs4 import BeautifulSoup
        try:
            homepage = f"https://{tool_name}.org"  # Simplified
            response = requests.get(homepage, timeout=self.config.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                title_text = title.get_text() if title else tool_name
                description = None
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content')
                metadata = UnifiedMetadata(
                    name=tool_name,
                    display_name=title_text,
                    description=description,
                    homepage=homepage,
                    category=ToolCategory.GENERIC,
                    source_priority="online"
                )
                metadata.add_installation_method(
                    method="web",
                    command=f"Visit {homepage} for installation instructions",
                    description=f"Install {tool_name} from official website"
                )
                return metadata
        except Exception as e:
            logging.warning(f"Failed to fetch {tool_name} from web: {e}")
        return None
    def get_priority(self) -> int:
        return 50  # Lower priority (fallback)
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.GENERIC]

def main():
    print("=== Unified MetadataFetcher Example ===\n")
    config = FetcherConfig(
        output_format="json",
        output_directory="example_outputs",
        request_delay=0.5,
        timeout=5.0
    )
    registry = FetcherRegistry(config)
    # Register the new PyPIFetcher, GitHubFetcher, and the fallback ExampleWebFetcher
    registry.register_class(PyPIFetcher)
    registry.register_class(GitHubFetcher)
    registry.register_class(ExampleWebFetcher)
    print(f"Registered {len(registry.get_all_fetchers())} fetchers:")
    for fetcher in registry.get_all_fetchers():
        print(f"  - {fetcher.name} (priority: {fetcher.get_priority()})")
    print(f"\nRegistry statistics: {registry.get_statistics()}")
    test_tools = ["pandas", "numpy", "flask", "git"]
    for tool_name in test_tools:
        print(f"\n--- Fetching metadata for {tool_name} ---")
        try:
            metadata = registry.fetch_metadata(tool_name)
            print(f"Name: {metadata.name}")
            print(f"Display Name: {metadata.display_name}")
            print(f"Description: {metadata.description[:100]}{'...' if len(metadata.description or '') > 100 else ''}")
            print(f"Category: {metadata.category.value}")
            print(f"Homepage: {metadata.homepage}")
            print(f"Documentation: {metadata.documentation}")
            print(f"Installation Methods: {len(metadata.installation_methods)}")
            print(f"Sources: {metadata.sources}")
            print(f"Fetch Duration: {metadata.fetch_duration:.2f}s")
            print(f"Is Complete: {metadata.is_complete()}")
            output_path = config.create_output_path(tool_name)
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Saved to: {output_path}")
            # Also save as YAML
            yaml_path = output_path.rsplit('.', 1)[0] + '.yaml'
            save_to_yaml(metadata, yaml_path)
            print(f"Saved to: {yaml_path}")
        except Exception as e:
            print(f"Error fetching {tool_name}: {e}")
    print("\n=== Example completed ===")

if __name__ == "__main__":
    main() 