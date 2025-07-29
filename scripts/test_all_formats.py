#!/usr/bin/env python3
"""
Comprehensive test script for all output formats with all 18 tools.
Tests the codebase with all available output formats for each tool.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.core.export_formats import get_available_formats, save_to_txt, save_to_docx, save_to_pdf
from metadata.core.basic import save_to_json, save_to_yaml
from metadata.core.fetchers.main_fetcher import MainFetcher

def load_tool_data():
    """Load tool descriptions and classifications."""
    try:
        with open('tool_descriptions.yaml', 'r', encoding='utf-8') as f:
            tool_descriptions = yaml.safe_load(f)
        
        with open('tool_classification.yaml', 'r', encoding='utf-8') as f:
            tool_classifications = yaml.safe_load(f)
        
        return tool_descriptions, tool_classifications
    except Exception as e:
        print(f"❌ Error loading tool data: {e}")
        return None, None

def get_all_tools():
    """Get list of all 18 tools from classifications."""
    tool_classifications, _ = load_tool_data()
    if not tool_classifications:
        return []
    
    return list(tool_classifications.keys())

def create_sample_data(tool_name, category):
    """Create sample metadata for testing."""
    return {
        "tool_name": tool_name,
        "category": category,
        "basic_info": {
            "tool_name": tool_name,
            "overview_description": f"Sample overview for {tool_name}",
            "key_features": [
                f"Feature 1 for {tool_name}",
                f"Feature 2 for {tool_name}",
                f"Feature 3 for {tool_name}"
            ],
            "use_cases": [
                f"Use case 1 for {tool_name}",
                f"Use case 2 for {tool_name}"
            ],
            "supported_platforms": ["Windows", "macOS", "Linux"]
        },
        "technical_specs": {
            "dependencies": [f"Dependency 1 for {tool_name}", f"Dependency 2 for {tool_name}"],
            "system_requirements": f"System requirements for {tool_name}",
            "performance_considerations": f"Performance considerations for {tool_name}",
            "supported_languages": ["Python", "JavaScript"],
            "supported_file_formats": ["JSON", "CSV", "XML"],
            "hardware_requirements": ["8GB RAM", "2GB Storage"],
            "network_requirements": ["Internet connection", "API access"]
        },
        "setup_info": {
            "installation_setup": f"Installation setup for {tool_name}",
            "configuration_guide": f"Configuration guide for {tool_name}",
            "quick_start_tutorial": f"Quick start tutorial for {tool_name}",
            "installation_commands": f"pip install {tool_name.lower()}",
            "setup_steps": [
                f"Step 1: Install {tool_name}",
                f"Step 2: Configure {tool_name}",
                f"Step 3: Test {tool_name}"
            ],
            "verification_commands": f"python -c 'import {tool_name.lower()}'",
            "environment_setup": f"Environment setup for {tool_name}",
            "dependency_management": f"Dependency management for {tool_name}"
        },
        "documentation": {
            "official_documentation": f"https://docs.{tool_name.lower()}.com",
            "api_reference": f"https://api.{tool_name.lower()}.com",
            "tutorials": f"https://tutorials.{tool_name.lower()}.com",
            "video_tutorials": f"https://videos.{tool_name.lower()}.com",
            "sample_projects": f"https://samples.{tool_name.lower()}.com"
        },
        "community": {
            "community_forums": f"https://community.{tool_name.lower()}.com",
            "github_repository": f"https://github.com/{tool_name.lower()}",
            "stack_overflow_tags": f"https://stackoverflow.com/questions/tagged/{tool_name.lower()}",
            "support_channels": f"https://support.{tool_name.lower()}.com",
            "user_groups": f"https://groups.{tool_name.lower()}.com"
        },
        "legal_versioning": {
            "license_type": "MIT License",
            "version": "1.0.0",
            "release_date": "2024-01-01",
            "update_policy": "Monthly updates",
            "end_of_life": "2026-01-01"
        },
        "references": {
            "official_website": f"https://{tool_name.lower()}.com",
            "download_links": f"https://download.{tool_name.lower()}.com",
            "demo_links": f"https://demo.{tool_name.lower()}.com"
        }
    }

def test_single_format(tool_name, category, format_name, output_dir):
    """Test a single format for a tool."""
    try:
        # Create sample data
        data = create_sample_data(tool_name, category)
        
        # Generate output filename
        filename = f"{tool_name.lower()}.{format_name}"
        output_path = os.path.join(output_dir, format_name, filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save in the specified format
        if format_name == 'json':
            save_to_json(data, output_path)
        elif format_name == 'yaml':
            save_to_yaml(data, output_path)
        elif format_name == 'txt':
            save_to_txt(data, output_path)
        elif format_name == 'docx':
            save_to_docx(data, output_path)
        elif format_name == 'pdf':
            save_to_pdf(data, output_path)
        
        return True, output_path
    except Exception as e:
        return False, str(e)

def test_all_formats():
    """Test all formats for all tools."""
    print("🚀 Starting comprehensive format testing...")
    print("=" * 60)
    
    # Load tool data
    tool_descriptions, tool_classifications = load_tool_data()
    if not tool_descriptions or not tool_classifications:
        print("❌ Failed to load tool data")
        return
    
    # Get all tools
    tools = get_all_tools()
    print(f"📋 Testing {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool}")
    
    # Get all formats
    formats = get_available_formats()
    print(f"\n📄 Testing {len(formats)} formats:")
    for fmt in formats:
        print(f"  - {fmt}")
    
    print("\n" + "=" * 60)
    
    # Test results tracking
    results = {
        'total_tests': 0,
        'successful_tests': 0,
        'failed_tests': 0,
        'tool_results': {},
        'format_results': {}
    }
    
    # Initialize format results
    for fmt in formats:
        results['format_results'][fmt] = {'success': 0, 'failed': 0}
    
    # Test each tool with each format
    for tool_name in tools:
        print(f"\n🔧 Testing tool: {tool_name}")
        
        # Get category for the tool
        category = tool_classifications.get(tool_name, ["Unknown"])[0]
        
        results['tool_results'][tool_name] = {'success': 0, 'failed': 0}
        
        for format_name in formats:
            print(f"  📄 Testing format: {format_name}")
            
            success, result = test_single_format(tool_name, category, format_name, "outputs")
            
            if success:
                print(f"    ✅ Success: {result}")
                results['successful_tests'] += 1
                results['tool_results'][tool_name]['success'] += 1
                results['format_results'][format_name]['success'] += 1
            else:
                print(f"    ❌ Failed: {result}")
                results['failed_tests'] += 1
                results['tool_results'][tool_name]['failed'] += 1
                results['format_results'][format_name]['failed'] += 1
            
            results['total_tests'] += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Total tests: {results['total_tests']}")
    print(f"Successful: {results['successful_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Success rate: {(results['successful_tests']/results['total_tests']*100):.1f}%")
    
    print("\n📋 Results by Tool:")
    for tool, result in results['tool_results'].items():
        success_rate = (result['success'] / (result['success'] + result['failed'])) * 100
        print(f"  {tool}: {result['success']}/{result['success'] + result['failed']} ({success_rate:.1f}%)")
    
    print("\n📄 Results by Format:")
    for fmt, result in results['format_results'].items():
        if result['success'] + result['failed'] > 0:
            success_rate = (result['success'] / (result['success'] + result['failed'])) * 100
            print(f"  {fmt}: {result['success']}/{result['success'] + result['failed']} ({success_rate:.1f}%)")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"testresults/test_results_{timestamp}.json"
    
    # Ensure testresults directory exists
    os.makedirs("testresults", exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    test_all_formats() 