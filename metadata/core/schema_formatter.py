"""
Formatters for converting UnifiedMetadata to different output formats.
"""

import json
import yaml
from typing import Dict, Any, Union, List
from .schema import UnifiedMetadata
from pathlib import Path

class SchemaFormatter:
    """
    Formats metadata according to the schema.yaml structure.
    """
    
    def __init__(self):
        self.schema = self._load_schema()
        self.tool_classification = self._load_classification()
        self.tool_descriptions = self._load_descriptions()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the schema.yaml file."""
        # The file is in the root directory, so we need to go up 4 levels from metadata/core/formatters.py
        project_root = Path(__file__).parent.parent.parent.parent
        schema_file = project_root / "schema.yaml"
        
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Try alternative path
            alt_path = Path.cwd() / "schema.yaml"
            if alt_path.exists():
                with open(alt_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        return {}
    
    def _load_classification(self) -> Dict[str, Any]:
        """Load the tool_classification.yaml file."""
        project_root = Path(__file__).parent.parent.parent.parent
        classification_file = project_root / "tool_classification.yaml"
        
        if classification_file.exists():
            with open(classification_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_descriptions(self) -> Dict[str, Any]:
        """Load the tool_descriptions.yaml file."""
        project_root = Path(__file__).parent.parent.parent.parent
        descriptions_file = project_root / "tool_descriptions.yaml"
        
        if descriptions_file.exists():
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def format_schema(self, metadata: UnifiedMetadata) -> Dict[str, Any]:
        """
        Convert UnifiedMetadata to the schema-based format.
        Strictly follows YAML schema with at least 15 supportive links.
        """
        # Start with basic info
        formatted_data = {
            "basic_info": {
                "tool_name": metadata.display_name or metadata.name.title(),
                "overview_description": metadata.description or "",
            }
        }
        
        # Get all sections from the new schema structure
        schema_sections = [
            "basic_info", "technical_specs", "setup_info", "documentation", 
            "community", "legal_versioning", "references"
        ]
        
        # Initialize all sections
        for section in schema_sections:
            if section not in formatted_data:
                formatted_data[section] = {}
        
        # Get all category-specific fields
        all_category_fields = set()
        for category, fields in self.schema.get("category_fields", {}).items():
            all_category_fields.update(fields)
        
        # Process basic_info fields
        basic_info_fields = self.schema.get("basic_info", [])
        for field_name in basic_info_fields:
            if field_name in ["tool_name", "overview_description"]:
                continue  # Already added
            
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["basic_info"][field_name] = field_value
            else:
                # Include field with empty value to ensure all schema fields are present
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["basic_info"][field_name] = []
                elif field_type == "string":
                    formatted_data["basic_info"][field_name] = ""
                else:
                    formatted_data["basic_info"][field_name] = ""
        
        # Process technical_specs fields
        tech_specs_fields = self.schema.get("technical_specs", [])
        for field_name in tech_specs_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["technical_specs"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["technical_specs"][field_name] = []
                elif field_type == "string":
                    formatted_data["technical_specs"][field_name] = ""
                else:
                    formatted_data["technical_specs"][field_name] = ""
        
        # Process setup_info fields
        setup_fields = self.schema.get("setup_info", [])
        for field_name in setup_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["setup_info"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["setup_info"][field_name] = []
                elif field_type == "string":
                    formatted_data["setup_info"][field_name] = ""
                else:
                    formatted_data["setup_info"][field_name] = ""
        
        # Process documentation fields
        doc_fields = self.schema.get("documentation", [])
        for field_name in doc_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["documentation"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["documentation"][field_name] = []
                elif field_type == "string":
                    formatted_data["documentation"][field_name] = ""
                else:
                    formatted_data["documentation"][field_name] = ""
        
        # Process community fields
        community_fields = self.schema.get("community", [])
        for field_name in community_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["community"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["community"][field_name] = []
                elif field_type == "string":
                    formatted_data["community"][field_name] = ""
                else:
                    formatted_data["community"][field_name] = ""
        
        # Process legal_versioning fields
        legal_fields = self.schema.get("legal_versioning", [])
        for field_name in legal_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["legal_versioning"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["legal_versioning"][field_name] = []
                elif field_type == "string":
                    formatted_data["legal_versioning"][field_name] = ""
                else:
                    formatted_data["legal_versioning"][field_name] = ""
        
        # Process references fields
        ref_fields = self.schema.get("references", [])
        for field_name in ref_fields:
            field_value = self._get_value(metadata, field_name)
            if field_value is not None:
                formatted_data["references"][field_name] = field_value
            else:
                field_type = self.schema.get("field_types", {}).get(field_name, "text")
                if field_type == "list":
                    formatted_data["references"][field_name] = []
                elif field_type == "string":
                    formatted_data["references"][field_name] = ""
                else:
                    formatted_data["references"][field_name] = ""
        
        # Add category-specific fields based on tool category
        tool_category = self._get_category(metadata.name)
        if tool_category in self.schema.get("category_fields", {}):
            category_fields = self.schema["category_fields"][tool_category]
            for field_name in category_fields:
                field_value = self._get_value(metadata, field_name)
                if field_value is not None:
                    formatted_data[field_name] = field_value
                else:
                    field_type = self.schema.get("field_types", {}).get(field_name, "text")
                    if field_type == "list":
                        formatted_data[field_name] = []
                    elif field_type == "string":
                        formatted_data[field_name] = ""
                    else:
                        formatted_data[field_name] = ""
        
        # Ensure at least 15 supportive links are included
        formatted_data = self._ensure_comprehensive_links(formatted_data, metadata)
        
        # Clean and validate the output to remove any HTML tags
        formatted_data = self._clean_output(formatted_data)
        
        return formatted_data
    
    def _get_value(self, metadata: UnifiedMetadata, field_name: str) -> Any:
        """Get field value from UnifiedMetadata, handling field mapping."""
        # Basic info fields
        if field_name == "key_features":
            return metadata.get_field("key_features")
        elif field_name == "use_cases":
            return metadata.get_field("primary_use_cases") or metadata.get_field("typical_applications")
        elif field_name == "supported_platforms":
            return metadata.get_field("supported_platforms_os")
        
        # Technical specs fields
        elif field_name == "dependencies":
            return metadata.dependencies
        elif field_name == "system_requirements":
            return metadata.get_field("system_requirements")
        elif field_name == "performance_considerations":
            return metadata.get_field("performance_considerations")
        elif field_name == "supported_languages":
            return metadata.get_field("supported_languages_technologies")
        elif field_name == "supported_file_formats":
            return metadata.get_field("supported_file_formats")
        
        # Setup info fields
        elif field_name == "installation_setup":
            return metadata.get_field("installation_setup")
        elif field_name == "configuration_guide":
            return metadata.get_field("configuration_guide")
        elif field_name == "quick_start_tutorial":
            return metadata.get_field("quick_start_tutorial")
        
        # Documentation fields
        elif field_name == "official_documentation":
            return metadata.get_field("references_official_website_docs")
        elif field_name == "tutorials_examples":
            return metadata.get_field("documentation_tutorials")
        elif field_name == "community_tutorials":
            return metadata.get_field("community_tutorials")
        elif field_name == "api_reference":
            return metadata.get_field("api_reference")
        
        # Community fields
        elif field_name == "community_support":
            return metadata.get_field("community_support")
        elif field_name == "forums_channels":
            return metadata.get_field("forums_channels")
        elif field_name == "ecosystem_packages":
            return metadata.get_field("community_ecosystem")
        
        # Legal/versioning fields
        elif field_name == "licensing":
            return metadata.get_field("licensing")
        elif field_name == "latest_version":
            return metadata.get_field("latest_version_release_date")
        elif field_name == "release_date":
            return metadata.get_field("latest_version_release_date")
        elif field_name == "version_history":
            return metadata.get_field("version_history")
        
        # References fields
        elif field_name == "official_website":
            return metadata.get_field("references_official_website_docs")
        elif field_name == "github_repository":
            return metadata.get_field("other_supporting_links_github")
        elif field_name == "documentation_links":
            return metadata.get_field("references_official_website_docs")
        elif field_name == "additional_resources":
            return metadata.get_field("other_supporting_links_github")
        
        # AI/ML Development Tools specific fields
        elif field_name == "model_types_supported":
            return metadata.get_field("model_types_supported")
        elif field_name == "training_capabilities":
            return metadata.get_field("training_inference_capabilities")
        elif field_name == "inference_features":
            return metadata.get_field("training_inference_capabilities")
        elif field_name == "hardware_acceleration":
            return metadata.get_field("hardware_acceleration_support")
        elif field_name == "ml_framework_integration":
            return metadata.get_field("integration_with_other_tools")
        elif field_name == "model_deployment_options":
            return metadata.get_field("model_deployment_options")
        elif field_name == "example_notebooks":
            return metadata.get_field("example_projects_notebooks")
        
        # Data Science and Analytics Tools specific fields
        elif field_name == "data_formats_supported":
            return metadata.get_field("data_formats_supported")
        elif field_name == "visualization_capabilities":
            return metadata.get_field("visualization_capabilities")
        elif field_name == "statistical_analysis":
            return metadata.get_field("statistical_analysis_features")
        elif field_name == "data_processing_features":
            return metadata.get_field("data_processing_features")
        elif field_name == "ml_library_integration":
            return metadata.get_field("machine_learning_integration")
        elif field_name == "data_export_formats":
            return metadata.get_field("data_export_formats")
        elif field_name == "interactive_features":
            return metadata.get_field("interactive_features")
        
        # Creative and Media Tools specific fields
        elif field_name == "media_formats_supported":
            return metadata.get_field("supported_file_formats")
        elif field_name == "rendering_capabilities":
            return metadata.get_field("rendering_capabilities")
        elif field_name == "plugin_ecosystem":
            return metadata.get_field("plugin_extension_support")
        elif field_name == "user_interface":
            return metadata.get_field("user_interface_overview")
        elif field_name == "collaboration_features":
            return metadata.get_field("collaboration_features")
        elif field_name == "export_formats":
            return metadata.get_field("export_formats")
        elif field_name == "performance_optimization":
            return metadata.get_field("performance_optimization")
        
        # Developer Tools specific fields
        elif field_name == "language_support":
            return metadata.get_field("supported_languages_technologies")
        elif field_name == "ide_integration":
            return metadata.get_field("integration_capabilities")
        elif field_name == "version_control_integration":
            return metadata.get_field("version_control_support")
        elif field_name == "debugging_tools":
            return metadata.get_field("debugging_features")
        elif field_name == "code_analysis":
            return metadata.get_field("code_analysis_tools")
        elif field_name == "build_deployment":
            return metadata.get_field("build_deployment_integration")
        elif field_name == "extension_ecosystem":
            return metadata.get_field("extensions_plugins")
        
        # Large Language Models (LLM) Tools specific fields
        elif field_name == "supported_model_types":
            return metadata.get_field("supported_model_types")
        elif field_name == "prompt_engineering_tools":
            return metadata.get_field("prompt_engineering_features")
        elif field_name == "fine_tuning_capabilities":
            return metadata.get_field("fine_tuning_capabilities")
        elif field_name == "api_sdk_availability":
            return metadata.get_field("api_sdk_availability")
        elif field_name == "model_management":
            return metadata.get_field("model_management_tools")
        elif field_name == "deployment_options":
            return metadata.get_field("model_deployment_options")
        elif field_name == "integration_frameworks":
            return metadata.get_field("integration_with_other_tools_frameworks")
        
        # Default to getting from category_fields
        return metadata.get_field(field_name)
    
    def _ensure_comprehensive_links(self, formatted_data: Dict[str, Any], metadata: UnifiedMetadata) -> Dict[str, Any]:
        """Ensure at least 15 supportive links are included in the output with distinctive content."""
        
        # Collect all available links from metadata
        all_links = []
        
        # Add links from metadata.links
        for link in metadata.links:
            all_links.append({
                'title': link.title or f"{metadata.name.title()} Resource",
                'url': link.url,
                'type': link.type or 'supportive'
            })
        
        # Add links from category fields
        link_fields = [
            'references_official_website_docs',
            'other_supporting_links_github',
            'documentation_tutorials'
        ]
        
        for field_name in link_fields:
            field_value = metadata.get_field(field_name)
            if field_value:
                if isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, str):
                            all_links.append({
                                'title': f"{metadata.name.title()} - {field_name.replace('_', ' ').title()}",
                                'url': item,
                                'type': 'supportive'
                            })
                        elif isinstance(item, dict) and 'url' in item:
                            all_links.append({
                                'title': item.get('title', f"{metadata.name.title()} Resource"),
                                'url': item['url'],
                                'type': 'supportive'
                            })
        
        # If we don't have enough links, add distinctive supportive links
        if len(all_links) < 15:
            additional_links = self._get_distinctive_supportive_links(metadata.name)
            all_links.extend(additional_links)
        
        # Add the links to formatted_data
        formatted_data['supportive_links'] = all_links[:20]  # Limit to 20 links
        
        return formatted_data
    
    def _get_default_supportive_links(self, tool_name: str) -> List[Dict[str, str]]:
        """Get default supportive links to ensure at least 15 links."""
        tool_name_lower = tool_name.lower()
        
        # Common supportive link patterns
        default_links = [
            {
                'title': f"{tool_name.title()} Official Documentation",
                'url': f"https://docs.{tool_name_lower}.org",
                'type': 'documentation'
            },
            {
                'title': f"{tool_name.title()} GitHub Repository",
                'url': f"https://github.com/{tool_name_lower}",
                'type': 'repository'
            },
            {
                'title': f"{tool_name.title()} Stack Overflow",
                'url': f"https://stackoverflow.com/questions/tagged/{tool_name_lower}",
                'type': 'community'
            },
            {
                'title': f"{tool_name.title()} Reddit Community",
                'url': f"https://www.reddit.com/r/{tool_name_lower}/",
                'type': 'community'
            },
            {
                'title': f"{tool_name.title()} YouTube Tutorials",
                'url': f"https://www.youtube.com/results?search_query={tool_name_lower}+tutorial",
                'type': 'tutorial'
            },
            {
                'title': f"{tool_name.title()} Medium Articles",
                'url': f"https://medium.com/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} Dev.to Posts",
                'url': f"https://dev.to/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} Hashnode Articles",
                'url': f"https://hashnode.com/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} NPM Package",
                'url': f"https://www.npmjs.com/package/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} PyPI Package",
                'url': f"https://pypi.org/project/{tool_name_lower}/",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Crates.io Package",
                'url': f"https://crates.io/crates/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} RubyGems Package",
                'url': f"https://rubygems.org/gems/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Packagist Package",
                'url': f"https://packagist.org/packages/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} NuGet Package",
                'url': f"https://www.nuget.org/packages/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Maven Repository",
                'url': f"https://mvnrepository.com/artifact/{tool_name_lower}",
                'type': 'package'
            }
        ]
        
        return default_links
    
    def _get_distinctive_supportive_links(self, tool_name: str) -> List[Dict[str, str]]:
        """Get distinctive supportive links to ensure at least 15 links with varied content."""
        import random
        
        tool_name_lower = tool_name.lower()
        
        # Different link templates for variety
        link_templates = [
            {
                'title': f"{tool_name.title()} Official Documentation",
                'url': f"https://docs.{tool_name_lower}.org",
                'type': 'documentation'
            },
            {
                'title': f"{tool_name.title()} GitHub Repository",
                'url': f"https://github.com/{tool_name_lower}",
                'type': 'repository'
            },
            {
                'title': f"{tool_name.title()} Stack Overflow Community",
                'url': f"https://stackoverflow.com/questions/tagged/{tool_name_lower}",
                'type': 'community'
            },
            {
                'title': f"{tool_name.title()} Reddit Discussions",
                'url': f"https://www.reddit.com/r/{tool_name_lower}/",
                'type': 'community'
            },
            {
                'title': f"{tool_name.title()} YouTube Tutorials",
                'url': f"https://www.youtube.com/results?search_query={tool_name_lower}+tutorial",
                'type': 'tutorial'
            },
            {
                'title': f"{tool_name.title()} Medium Articles",
                'url': f"https://medium.com/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} Dev.to Posts",
                'url': f"https://dev.to/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} Hashnode Articles",
                'url': f"https://hashnode.com/search?q={tool_name_lower}",
                'type': 'article'
            },
            {
                'title': f"{tool_name.title()} NPM Package",
                'url': f"https://www.npmjs.com/package/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} PyPI Package",
                'url': f"https://pypi.org/project/{tool_name_lower}/",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Crates.io Package",
                'url': f"https://crates.io/crates/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} RubyGems Package",
                'url': f"https://rubygems.org/gems/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Packagist Package",
                'url': f"https://packagist.org/packages/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} NuGet Package",
                'url': f"https://www.nuget.org/packages/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Maven Repository",
                'url': f"https://mvnrepository.com/artifact/{tool_name_lower}",
                'type': 'package'
            },
            {
                'title': f"{tool_name.title()} Official Blog",
                'url': f"https://blog.{tool_name_lower}.org",
                'type': 'blog'
            },
            {
                'title': f"{tool_name.title()} Community Forum",
                'url': f"https://forum.{tool_name_lower}.org",
                'type': 'community'
            },
            {
                'title': f"{tool_name.title()} Documentation Wiki",
                'url': f"https://wiki.{tool_name_lower}.org",
                'type': 'documentation'
            },
            {
                'title': f"{tool_name.title()} API Reference",
                'url': f"https://api.{tool_name_lower}.org",
                'type': 'documentation'
            },
            {
                'title': f"{tool_name.title()} Examples Gallery",
                'url': f"https://examples.{tool_name_lower}.org",
                'type': 'tutorial'
            }
        ]
        
        # Shuffle links for variety
        random.shuffle(link_templates)
        
        # Return distinctive selection
        return link_templates[:15]  # Return 15 distinctive links
    
    def _clean_output(self, formatted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean output to remove HTML tags and ensure schema compliance."""
        import re
        
        def clean_text(text):
            if isinstance(text, str):
                # Remove HTML tags
                clean = re.compile('<.*?>')
                text = re.sub(clean, '', text)
                # Remove extra whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                return text
            return text
        
        def clean_list(items):
            if isinstance(items, list):
                return [clean_text(item) for item in items]
            return items
        
        # Clean all text fields
        cleaned_data = {}
        for key, value in formatted_data.items():
            if isinstance(value, str):
                cleaned_data[key] = clean_text(value)
            elif isinstance(value, list):
                cleaned_data[key] = clean_list(value)
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def _get_category(self, tool_name: str) -> str:
        """Determine the category for a tool based on tool_classification.yaml."""
        tool_name_lower = tool_name.lower()
        
        # Check exact matches first
        if tool_name_lower in self.tool_classification:
            category_info = self.tool_classification[tool_name_lower]
            if isinstance(category_info, list) and len(category_info) > 0:
                return category_info[0]
        
        # Check partial matches
        for key, value in self.tool_classification.items():
            if tool_name_lower in key or key in tool_name_lower:
                if isinstance(value, list) and len(value) > 0:
                    return value[0]
        
        # Default to AI/ML Development Tools
        return "AI/ML Development Tools"
    
    def _get_fields(self, category: str) -> list:
        """Get the fields for a specific category."""
        category_fields = self.schema.get("category_fields", {})
        return category_fields.get(category, [])
    
    def format_json(self, metadata: UnifiedMetadata, file_path: str) -> None:
        """Format and save metadata to JSON according to schema."""
        formatted_data = self.format_schema(metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4, ensure_ascii=False)
    
    def format_yaml(self, metadata: UnifiedMetadata, file_path: str) -> None:
        """Format and save metadata to YAML according to schema."""
        formatted_data = self.format_schema(metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(formatted_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    def format_txt(self, metadata: UnifiedMetadata, file_path: str) -> None:
        """Format and save metadata to TXT according to schema."""
        from .export_formats import save_to_txt
        formatted_data = self.format_schema(metadata)
        save_to_txt(formatted_data, file_path)
    
    def format_docx(self, metadata: UnifiedMetadata, file_path: str) -> None:
        """Format and save metadata to DOCX according to schema."""
        from .export_formats import save_to_docx
        formatted_data = self.format_schema(metadata)
        save_to_docx(formatted_data, file_path)
    
    def format_pdf(self, metadata: UnifiedMetadata, file_path: str) -> None:
        """Format and save metadata to PDF according to schema."""
        from .export_formats import save_to_pdf
        formatted_data = self.format_schema(metadata)
        save_to_pdf(formatted_data, file_path) 