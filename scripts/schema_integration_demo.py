#!/usr/bin/env python3
"""
Demonstration of schema integration with metadata fetcher.
This script shows how to use the schema.yaml for dynamic field assignment
instead of hardcoded categories.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.schema_utils import SchemaManager, load_tool_classification, get_tool_category
import yaml
import json
from typing import Dict, Any


class SchemaAwareMetadataFetcher:
    """Metadata fetcher that uses schema for dynamic field assignment."""
    
    def __init__(self):
        """Initialize the schema-aware metadata fetcher."""
        self.schema_manager = SchemaManager()
        self.classification_map = load_tool_classification()
    
    def get_tool_fields(self, tool_name: str) -> Dict[str, Any]:
        """Get the appropriate fields for a tool based on its category.
        
        Args:
            tool_name: Name of the tool to get fields for
            
        Returns:
            Dictionary with field names and their descriptions
        """
        # Determine tool category
        category = get_tool_category(tool_name, self.classification_map)
        if not category:
            print(f"Warning: No category found for tool '{tool_name}'")
            return {}
        
        # Get fields for the category
        fields = self.schema_manager.get_fields_for_category(category)
        
        # Create field info dictionary
        field_info = {}
        for field in fields:
            description = self.schema_manager.get_field_description(field)
            field_type = self.schema_manager.get_field_type(field)
            field_info[field] = {
                'description': description,
                'type': field_type,
                'required': True
            }
        
        return field_info
    
    def generate_metadata_template(self, tool_name: str) -> Dict[str, Any]:
        """Generate a metadata template for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Template dictionary with appropriate fields
        """
        category = get_tool_category(tool_name, self.classification_map)
        if not category:
            print(f"Warning: No category found for tool '{tool_name}'")
            return {}
        
        template = self.schema_manager.generate_template(category)
        template['tool_name'] = tool_name
        template['category'] = category
        
        return template
    
    def validate_metadata(self, tool_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata against the schema.
        
        Args:
            tool_name: Name of the tool
            metadata: Metadata dictionary to validate
            
        Returns:
            Validation results
        """
        category = get_tool_category(tool_name, self.classification_map)
        if not category:
            return {
                'valid': False,
                'error': f"No category found for tool '{tool_name}'"
            }
        
        return self.schema_manager.validate_tool_data(metadata, category)
    
    def fetch_and_validate_metadata(self, tool_name: str) -> Dict[str, Any]:
        """Simulate fetching metadata and validating it.
        
        Args:
            tool_name: Name of the tool to fetch metadata for
            
        Returns:
            Dictionary with metadata and validation results
        """
        # This would normally call your actual metadata fetcher
        # For demo purposes, we'll create sample data
        sample_metadata = self._generate_sample_metadata(tool_name)
        
        # Validate the metadata
        validation = self.validate_metadata(tool_name, sample_metadata)
        
        return {
            'tool_name': tool_name,
            'metadata': sample_metadata,
            'validation': validation,
            'template': self.generate_metadata_template(tool_name)
        }
    
    def _generate_sample_metadata(self, tool_name: str) -> Dict[str, Any]:
        """Generate sample metadata for demonstration."""
        category = get_tool_category(tool_name, self.classification_map)
        
        if category == 'Data Science and Analytics Tools':
            return {
                'tool_name': tool_name,
                'overview_description': f'{tool_name} is a powerful data science library',
                'key_features': ['Data manipulation', 'Statistical analysis', 'Visualization'],
                'dependencies': ['numpy', 'scipy'],
                'typical_applications': ['Data analysis', 'Machine learning'],
                'data_formats_supported': ['CSV', 'Excel', 'JSON'],
                'visualization_capabilities': 'Advanced plotting and charting',
                'community_ecosystem': 'Large and active community',
                'licensing': 'MIT License',
                'latest_version_release_date': '2.1.0 (2024-01-15)'
            }
        elif category == 'AI/ML Development Tools':
            return {
                'tool_name': tool_name,
                'overview_description': f'{tool_name} is an AI/ML development framework',
                'key_features': ['Neural networks', 'Deep learning', 'GPU acceleration'],
                'dependencies': ['numpy', 'scipy', 'matplotlib'],
                'primary_use_cases': ['Computer vision', 'Natural language processing'],
                'supported_platforms_os': ['Linux', 'Windows', 'macOS'],
                'hardware_acceleration_support': 'CUDA, ROCm support',
                'licensing': 'Apache 2.0',
                'latest_version_release_date': '2.0.0 (2024-01-10)'
            }
        else:
            return {
                'tool_name': tool_name,
                'overview_description': f'{tool_name} is a development tool',
                'key_features': ['Feature 1', 'Feature 2'],
                'dependencies': ['dependency1'],
                'licensing': 'MIT License',
                'latest_version_release_date': '1.0.0 (2024-01-01)'
            }


def demonstrate_schema_integration():
    """Demonstrate the schema integration with example tools."""
    print("=== Schema Integration Demonstration ===\n")
    
    fetcher = SchemaAwareMetadataFetcher()
    
    # Test with different tool types
    test_tools = ['pandas', 'pytorch', 'blender', 'visual studio code', 'langchain']
    
    for tool in test_tools:
        print(f"\n--- {tool.upper()} ---")
        
        # Get fields for this tool
        fields = fetcher.get_tool_fields(tool)
        print(f"Category fields ({len(fields)} total):")
        for field_name, field_info in list(fields.items())[:5]:  # Show first 5
            print(f"  - {field_name} ({field_info['type']}): {field_info['description']}")
        if len(fields) > 5:
            print(f"  ... and {len(fields) - 5} more fields")
        
        # Generate template
        template = fetcher.generate_metadata_template(tool)
        print(f"\nTemplate generated with {len(template)} fields")
        
        # Fetch and validate sample metadata
        result = fetcher.fetch_and_validate_metadata(tool)
        
        print(f"\nValidation results:")
        validation = result['validation']
        print(f"  Valid: {validation['valid']}")
        if validation['missing_fields']:
            print(f"  Missing: {validation['missing_fields']}")
        if validation['type_errors']:
            print(f"  Type errors: {validation['type_errors']}")
        
        # Show sample metadata
        metadata = result['metadata']
        print(f"\nSample metadata:")
        for key, value in list(metadata.items())[:3]:  # Show first 3
            if isinstance(value, list):
                print(f"  {key}: {value[:2]}...")  # Show first 2 items
            else:
                print(f"  {key}: {value}")
        if len(metadata) > 3:
            print(f"  ... and {len(metadata) - 3} more fields")


def show_schema_benefits():
    """Show the benefits of using the schema approach."""
    print("\n=== Schema Benefits ===\n")
    
    print("1. DYNAMIC FIELD ASSIGNMENT:")
    print("   - No hardcoded categories in code")
    print("   - Easy to add new categories or modify existing ones")
    print("   - Consistent field structure across all tools")
    
    print("\n2. VALIDATION AND TYPE SAFETY:")
    print("   - Automatic field type validation")
    print("   - Missing field detection")
    print("   - Consistent data structure enforcement")
    
    print("\n3. FLEXIBILITY:")
    print("   - Easy to add new fields to categories")
    print("   - Common fields shared across all categories")
    print("   - Category-specific fields for specialized information")
    
    print("\n4. MAINTENANCE:")
    print("   - Single source of truth for field definitions")
    print("   - Easy to update field descriptions and types")
    print("   - Clear documentation of what each field means")
    
    print("\n5. INTEGRATION:")
    print("   - Works with existing tool classification")
    print("   - Can be easily integrated with metadata fetchers")
    print("   - Supports both validation and template generation")


if __name__ == "__main__":
    demonstrate_schema_integration()
    show_schema_benefits() 