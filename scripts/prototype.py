#!/usr/bin/env python3
"""
Process Prototype Tools Script
Generates comprehensive metadata for all tools in the SampleOutputs folder
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# DEPRECATED: This script uses old modules that no longer exist
# from metadata.fetchers.comprehensive_fetcher import process_all_prototype_tools, fetch_comprehensive_metadata, save_comprehensive_metadata_json

def main():
    """Main function to process all prototype tools."""
    
    print("=" * 80)
    print("PROTOTYPE TOOLS METADATA PROCESSOR")
    print("=" * 80)
    print()
    print("This script will generate comprehensive metadata for all tools")
    print("found in the SampleOutputs folder, matching the desired format.")
    print()
    
    # Process all prototype tools
    try:
        processed_tools = process_all_prototype_tools()
        
        print("\n" + "=" * 80)
        print("PROCESSING SUMMARY")
        print("=" * 80)
        
        if processed_tools:
            print(f"\nSuccessfully processed {len(processed_tools)} tools:")
            for tool, category, output_file in processed_tools:
                print(f"  ✓ {tool} ({category})")
                print(f"    Output: {output_file}")
            
            print(f"\nAll metadata files have been generated in the SampleOutputs directory.")
            print("The generated JSON files match the format of your prototype outputs.")
            
        else:
            print("No tools were processed successfully.")
            
    except Exception as e:
        print(f"\nError during processing: {e}")
        return 1
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review the generated JSON files in SampleOutputs/")
    print("2. Compare with your original prototype files")
    print("3. Update the fetcher logic if needed")
    print("4. Integrate the comprehensive fetcher into your main workflow")
    print()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 