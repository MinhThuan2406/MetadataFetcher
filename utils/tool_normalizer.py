"""
Tool name normalization utility.
Handles mapping different tool name variations to standardized names and display names.
"""

import re
from typing import Dict, Tuple, Optional

class ToolNormalizer:
    """Normalizes tool names and provides standardized display names."""
    
    def __init__(self):
        # Tool name variations mapping
        # Key: normalized tool name (for internal use)
        # Value: (display_name, aliases)
        self.tool_variations = {
            'visual_studio_code': (
                'Visual Studio Code (VSCode)',
                ['vscode', 'visualstudiocode', 'visual studio code', 'vs code', 'vsc']
            ),
            'git_version_control': (
                'Git (Version Control)',
                ['git', 'git version control', 'git (version control)', 'version control']
            ),
            'github_desktop': (
                'GitHub Desktop',
                ['githubdesktop', 'github desktop', 'github']
            ),
            'hugging_face_transformers': (
                'Hugging Face Transformers',
                ['huggingface', 'transformers', 'hugging face', 'hugging face transformers']
            ),
            'elgato_stream_deck': (
                'Elgato Stream Deck',
                ['elgatostreamdeck', 'elgato stream deck', 'stream deck', 'elgato']
            ),
            'jupyter_lab': (
                'JupyterLab',
                ['jupyterlab', 'jupyter lab', 'jupyter']
            ),
            'jupyter_notebook': (
                'Jupyter Notebook',
                ['jupyternotebook', 'jupyter notebook', 'notebook']
            ),
            'comfy_ui': (
                'ComfyUI',
                ['comfyui', 'comfy ui', 'comfy']
            )
        }
        
        # Create reverse mapping for quick lookup
        self.alias_to_normalized = {}
        for normalized_name, (display_name, aliases) in self.tool_variations.items():
            self.alias_to_normalized[normalized_name] = normalized_name
            for alias in aliases:
                self.alias_to_normalized[alias.lower()] = normalized_name
    
    def normalize_tool_name(self, tool_name: str) -> str:
        """
        Normalize a tool name to its standard internal name.
        
        Args:
            tool_name: The input tool name (any variation)
            
        Returns:
            The normalized tool name for internal use
        """
        if not tool_name:
            return tool_name
            
        # Clean the input
        cleaned_name = self._clean_tool_name(tool_name)
        
        # Check if we have a mapping for this tool
        if cleaned_name in self.alias_to_normalized:
            return self.alias_to_normalized[cleaned_name]
        
        # If no mapping found, return the cleaned name
        return cleaned_name
    
    def get_display_name(self, tool_name: str) -> str:
        """
        Get the standardized display name for a tool.
        
        Args:
            tool_name: The input tool name (any variation)
            
        Returns:
            The standardized display name
        """
        normalized_name = self.normalize_tool_name(tool_name)
        
        # Check if we have a display name mapping
        if normalized_name in self.tool_variations:
            return self.tool_variations[normalized_name][0]
        
        # If no mapping found, return the normalized name with proper casing
        return self._format_display_name(normalized_name)
    
    def get_aliases(self, tool_name: str) -> list:
        """
        Get all known aliases for a tool.
        
        Args:
            tool_name: The input tool name (any variation)
            
        Returns:
            List of all known aliases for the tool
        """
        normalized_name = self.normalize_tool_name(tool_name)
        
        if normalized_name in self.tool_variations:
            return self.tool_variations[normalized_name][1]
        
        return []
    
    def is_known_tool(self, tool_name: str) -> bool:
        """
        Check if a tool name is known (has any variations).
        
        Args:
            tool_name: The input tool name
            
        Returns:
            True if the tool is known, False otherwise
        """
        cleaned_name = self._clean_tool_name(tool_name)
        return cleaned_name in self.alias_to_normalized
    
    def get_all_known_tools(self) -> list:
        """
        Get all known normalized tool names.
        
        Returns:
            List of all known normalized tool names
        """
        return list(self.tool_variations.keys())
    
    def _clean_tool_name(self, tool_name: str) -> str:
        """
        Clean a tool name for comparison.
        
        Args:
            tool_name: The input tool name
            
        Returns:
            Cleaned tool name
        """
        if not tool_name:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        cleaned = tool_name.lower().strip()
        
        # Remove special characters except spaces and hyphens
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _format_display_name(self, tool_name: str) -> str:
        """
        Format a tool name for display with proper casing.
        
        Args:
            tool_name: The input tool name
            
        Returns:
            Formatted display name
        """
        if not tool_name:
            return ""
        
        # Split by underscores and hyphens
        parts = re.split(r'[_-]', tool_name)
        
        # Capitalize each part
        formatted_parts = []
        for part in parts:
            if part:
                # Handle special cases
                if part.lower() in ['ai', 'ml', 'api', 'sdk', 'ide', 'ui', 'ux']:
                    formatted_parts.append(part.upper())
                else:
                    formatted_parts.append(part.capitalize())
        
        return ' '.join(formatted_parts)

# Global instance for easy access
tool_normalizer = ToolNormalizer() 