"""
Unified Report Router for MetadataFetcher
This module routes different tool categories to their appropriate dedicated report generators.
"""

import json
import os
import yaml
from typing import Optional

# Import all category-specific report generators
from output_processor.ai_ml_reports import export_ai_ml_tool
from output_processor.data_science_reports import export_data_science_tool
from output_processor.creative_media_reports import export_creative_media_tool
from output_processor.developer_tools_reports import export_developer_tool
from output_processor.llm_tools_reports import export_llm_tool

class ReportRouter:
    """Routes tools to appropriate category-specific report generators"""
    
    def __init__(self):
        self.load_tool_classification()
        
    def load_tool_classification(self):
        """Load tool classification from YAML file"""
        try:
            with open('tool_classification.yaml', 'r', encoding='utf-8') as f:
                self.tool_classification = yaml.safe_load(f)
        except FileNotFoundError:
            print("[WARN] tool_classification.yaml not found. Using empty classification.")
            self.tool_classification = {}
            
    def normalize_tool_name(self, name):
        """Normalize tool name for comparison"""
        return ''.join(e for e in name.strip().lower().replace('-', ' ').replace('_', ' ') if e.isalnum())
        
    def get_tool_category(self, tool_name: str) -> Optional[str]:
        """Get the category for a given tool name"""
        normalized_name = self.normalize_tool_name(tool_name)
        
        # Direct lookup
        for tool_key, (category, tool_type) in self.tool_classification.items():
            if self.normalize_tool_name(tool_key) == normalized_name:
                return category
                
        # Check for partial matches or aliases
        for tool_key, (category, tool_type) in self.tool_classification.items():
            # Handle combined entries like "jupyterlab / jupyter notebook"
            if '/' in tool_key or ',' in tool_key:
                aliases = [k.strip() for k in tool_key.replace('/', ',').split(',')]
                for alias in aliases:
                    if self.normalize_tool_name(alias) == normalized_name:
                        return category
                        
        return None
        
    def detect_category_from_json(self, json_path: str) -> Optional[str]:
        """Detect category from JSON file content"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check if General Information contains Use Case
                general_info = data.get('General Information', {})
                use_case = general_info.get('Use Case')
                if use_case:
                    return use_case
                    
                # Check tool name against classification
                tool_name = general_info.get('Name')
                if tool_name:
                    category = self.get_tool_category(tool_name)
                    if category:
                        return category
                        
                # Check if it's creative media format
                if 'General Information' in data and 'Product Details' in data:
                    return "Creative and Media Tools"
                    
        except Exception as e:
            print(f"[WARN] Could not detect category from JSON: {e}")
            
        return None
        
    def route_to_category_generator(self, json_path: str, category: str) -> Optional[str]:
        """Route to appropriate category-specific generator"""
        category_mappings = {
            "AI/ML Development Tools": export_ai_ml_tool,
            "Data Science and Analytics Tools": export_data_science_tool,
            "Creative and Media Tools": export_creative_media_tool,
            "Developer Tools": export_developer_tool,
            "Large Language Models (LLM) Tools": export_llm_tool,
        }
        
        generator_func = category_mappings.get(category)
        if generator_func:
            print(f"[INFO] Routing to {category} generator")
            return generator_func(json_path)
        else:
            print(f"[WARN] No generator found for category: {category}")
            return None
            
    def generate_report(self, json_path: str, category: Optional[str] = None) -> Optional[str]:
        """Generate report using appropriate category-specific generator"""
        if not os.path.exists(json_path):
            print(f"[ERROR] JSON file not found: {json_path}")
            return None
            
        # Auto-detect category if not provided
        if not category:
            category = self.detect_category_from_json(json_path)
            
        if not category:
            print(f"[WARN] Could not determine category for {json_path}. Using Creative Media as fallback.")
            category = "Creative and Media Tools"
            
        print(f"[INFO] Generating report for category: {category}")
        return self.route_to_category_generator(json_path, category)

# Convenience functions for backward compatibility
def export_tool_report(json_path: str, category: Optional[str] = None) -> Optional[str]:
    """Main export function that routes to appropriate category generator"""
    router = ReportRouter()
    return router.generate_report(json_path, category)

def export_by_tool_name(tool_name: str, json_path: str) -> Optional[str]:
    """Export by tool name (auto-detects category)"""
    router = ReportRouter()
    category = router.get_tool_category(tool_name)
    return router.generate_report(json_path, category)

# Legacy compatibility functions
def json_to_professional_word(json_path: str):
    """Legacy function - routes to appropriate generator"""
    return export_tool_report(json_path)

def export_product_docx(json_path: str):
    """Legacy function - routes to appropriate generator"""
    return export_tool_report(json_path)

def export_borderline_docx(json_path: str):
    """Legacy function - routes to appropriate generator"""
    return export_tool_report(json_path)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_router.py <json_path> [category]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = export_tool_report(json_path, category)
    if result:
        print(f"Report generated successfully: {result}")
    else:
        print("Failed to generate report")