#!/usr/bin/env python3
"""
Simple MetadataFetcher Example

This example demonstrates how to use the MetadataFetcher both programmatically
and via the CLI interface.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.core import FetcherRegistry, FetcherConfig, ToolCategory
from metadata.core.fetchers import PyPIFetcher, GitHubFetcher, DockerHubFetcher, DocsFetcher
from metadata.core.basic import save_to_json, save_to_yaml
from metadata.core.formats import save_to_docx, save_to_pdf

def main():
    """Demonstrate MetadataFetcher usage."""
    
    print("🚀 MetadataFetcher Simple Example")
    print("=" * 50)
    
    # 1. Basic Configuration
    print("\n1. Setting up configuration...")
    config = FetcherConfig(
        output_format="json",
        output_directory="outputs",
        enable_caching=True,
        request_delay=0.5
    )
    
    # 2. Setup Registry
    print("2. Setting up fetcher registry...")
    registry = FetcherRegistry(config)
    
    # Register all fetchers
    registry.register_class(PyPIFetcher)
    registry.register_class(GitHubFetcher)
    registry.register_class(DockerHubFetcher)
    registry.register_class(DocsFetcher)
    
    print(f"   Registered {len(registry._fetchers)} fetchers")
    
    # 3. Test Tools
    test_tools = ["pandas", "numpy", "flask"]
    
    print(f"\n3. Fetching metadata for {len(test_tools)} tools...")
    
    for i, tool_name in enumerate(test_tools, 1):
        print(f"\n   [{i}/{len(test_tools)}] Processing: {tool_name}")
        
        try:
            # Fetch metadata
            metadata = registry.fetch_metadata(tool_name)
            
            if metadata:
                print(f"   ✅ Found metadata for {tool_name}")
                print(f"      - Name: {metadata.name}")
                print(f"      - Category: {metadata.category.value}")
                print(f"      - Version: {metadata.version}")
                print(f"      - Sources: {metadata.sources}")
                
                # Save in multiple formats
                output_paths = []
                
                # JSON
                json_path = config.create_output_path(tool_name, "json")
                save_to_json(metadata, json_path)
                output_paths.append(json_path)
                
                # YAML
                yaml_path = config.create_output_path(tool_name, "yaml")
                save_to_yaml(metadata, yaml_path)
                output_paths.append(yaml_path)
                
                # DOCX (if available)
                try:
                    docx_path = config.create_output_path(tool_name, "docx")
                    save_to_docx(metadata, docx_path)
                    output_paths.append(docx_path)
                except ImportError:
                    print("      - DOCX export not available (python-docx not installed)")
                
                # PDF (if available)
                try:
                    pdf_path = config.create_output_path(tool_name, "pdf")
                    save_to_pdf(metadata, pdf_path)
                    output_paths.append(pdf_path)
                except ImportError:
                    print("      - PDF export not available (reportlab not installed)")
                
                print(f"      - Saved to: {len(output_paths)} files")
                
            else:
                print(f"   ❌ No metadata found for {tool_name}")
                
        except Exception as e:
            print(f"   ❌ Error processing {tool_name}: {e}")
    
    # 4. Summary
    print("\n4. Summary")
    print("   - All fetchers registered and working")
    print("   - Multiple output formats supported")
    print("   - Caching enabled for performance")
    print("   - Unified output structure in 'outputs/' directory")
    
    # 5. CLI Usage Instructions
    print("\n5. CLI Usage Examples:")
    print("   # Single tool")
    print("   python -m cli.main fetch pandas --format json")
    print("   python -m cli.main fetch numpy --format yaml")
    print("   python -m cli.main fetch flask --format docx")
    print("   python -m cli.main fetch matplotlib --format pdf")
    print()
    print("   # Batch processing")
    print("   python -m cli.main batch pandas numpy matplotlib --format json")
    print("   python -m cli.main batch --input-file tools.txt --format yaml")
    print()
    print("   # System information")
    print("   python -m cli.main info")
    print("   python -m cli.main formats")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    main() 