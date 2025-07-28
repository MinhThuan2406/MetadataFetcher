#!/usr/bin/env python3
"""
Schema utilities for dynamic field assignment based on tool categories.
This module provides functions to load and use the schema.yaml for flexible
field mapping instead of hardcoded categories.
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class SchemaManager:
    """Manages the schema for dynamic field assignment."""
    
    def __init__(self, schema_path: str = "schema.yaml"):
        """Initialize the schema manager.
        
        Args:
            schema_path: Path to the schema.yaml file
        """
        self.schema_path = schema_path
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the schema from YAML file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in schema file: {e}")
    
    def get_fields_for_category(self, category: str) -> List[str]:
        """Get all fields for a specific category.
        
        Args:
            category: The tool category (e.g., 'AI_ML_Development_Tools')
            
        Returns:
            List of field names for the category
        """
        if category not in self.schema.get('category_fields', {}):
            raise ValueError(f"Unknown category: {category}")
        
        common_fields = self.schema.get('common_fields', [])
        category_fields = self.schema.get('category_fields', {}).get(category, [])
        
        return common_fields + category_fields
    
    def get_field_description(self, field_name: str) -> Optional[str]:
        """Get the description for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field description or None if not found
        """
        return self.schema.get('field_descriptions', {}).get(field_name)
    
    def get_field_type(self, field_name: str) -> Optional[str]:
        """Get the expected data type for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field type ('string', 'text', 'list') or None if not found
        """
        return self.schema.get('field_types', {}).get(field_name)
    
    def validate_tool_data(self, tool_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Validate tool data against the schema.
        
        Args:
            tool_data: Dictionary containing tool information
            category: Tool category for field validation
            
        Returns:
            Dictionary with validation results
        """
        expected_fields = self.get_fields_for_category(category)
        validation_results = {
            'valid': True,
            'missing_fields': [],
            'extra_fields': [],
            'type_errors': [],
            'warnings': []
        }
        
        # Check for missing required fields
        for field in expected_fields:
            if field not in tool_data:
                validation_results['missing_fields'].append(field)
                validation_results['valid'] = False
        
        # Check for extra fields
        for field in tool_data.keys():
            if field not in expected_fields:
                validation_results['extra_fields'].append(field)
                validation_results['warnings'].append(f"Unexpected field: {field}")
        
        # Check field types
        for field, value in tool_data.items():
            expected_type = self.get_field_type(field)
            if expected_type:
                if expected_type == 'list' and not isinstance(value, list):
                    validation_results['type_errors'].append(f"{field}: expected list, got {type(value).__name__}")
                    validation_results['valid'] = False
                elif expected_type == 'string' and not isinstance(value, str):
                    validation_results['type_errors'].append(f"{field}: expected string, got {type(value).__name__}")
                    validation_results['valid'] = False
        
        return validation_results
    
    def generate_template(self, category: str) -> Dict[str, Any]:
        """Generate a template dictionary for a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            Template dictionary with all required fields
        """
        fields = self.get_fields_for_category(category)
        template = {}
        
        for field in fields:
            field_type = self.get_field_type(field)
            if field_type == 'list':
                template[field] = []
            elif field_type == 'string':
                template[field] = ""
            else:
                template[field] = ""
        
        return template
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories.
        
        Returns:
            List of category names
        """
        return list(self.schema.get('category_fields', {}).keys())


def load_tool_classification() -> Dict[str, List[str]]:
    """Load the tool classification mapping.
    
    Returns:
        Dictionary mapping tool names to categories
    """
    try:
        with open('tool_classification.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Warning: tool_classification.yaml not found")
        return {}


def get_tool_category(tool_name: str, classification_map: Dict[str, List[str]]) -> Optional[str]:
    """Get the category for a specific tool.
    
    Args:
        tool_name: Name of the tool
        classification_map: Mapping from tool names to categories
        
    Returns:
        Category name or None if not found
    """
    # Direct match
    if tool_name in classification_map:
        return classification_map[tool_name][0]
    
    # Fuzzy matching (case-insensitive)
    tool_name_lower = tool_name.lower()
    for key, value in classification_map.items():
        if tool_name_lower in key.lower() or key.lower() in tool_name_lower:
            return value[0]
    
    return None


def example_usage():
    """Example usage of the schema utilities."""
    print("=== Schema Utilities Example ===\n")
    
    # Initialize schema manager
    schema_manager = SchemaManager()
    
    # Get all categories
    categories = schema_manager.get_all_categories()
    print(f"Available categories: {categories}\n")
    
    # Example: Get fields for AI/ML tools
    ai_ml_fields = schema_manager.get_fields_for_category('AI/ML Development Tools')
    print(f"AI/ML Development Tools fields ({len(ai_ml_fields)} total):")
    for field in ai_ml_fields:
        desc = schema_manager.get_field_description(field)
        field_type = schema_manager.get_field_type(field)
        print(f"  - {field} ({field_type}): {desc}")
    print()
    
    # Example: Generate template
    template = schema_manager.generate_template('Data Science and Analytics Tools')
    print("Data Science template:")
    for key, value in template.items():
        print(f"  {key}: {value}")
    print()
    
    # Example: Validate tool data
    sample_tool_data = {
        'tool_name': 'pandas',
        'overview_description': 'Data manipulation library',
        'key_features': ['DataFrame', 'Series', 'Data analysis'],
        'dependencies': ['numpy', 'python-dateutil'],
        'typical_applications': ['Data analysis', 'Data cleaning'],
        'data_formats_supported': ['CSV', 'Excel', 'JSON']
    }
    
    validation = schema_manager.validate_tool_data(sample_tool_data, 'Data Science and Analytics Tools')
    print("Validation results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Missing fields: {validation['missing_fields']}")
    print(f"  Extra fields: {validation['extra_fields']}")
    print(f"  Type errors: {validation['type_errors']}")
    print(f"  Warnings: {validation['warnings']}")


if __name__ == "__main__":
    example_usage() 