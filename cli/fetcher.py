"""
Unified metadata fetcher with improved information fetching logic.
"""

import click
import sys
import requests
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.core import FetcherRegistry, FetcherConfig, ToolCategory
from metadata.core.fetchers import PyPIFetcher, GitHubFetcher, DockerHubFetcher, DocsFetcher, GoogleCSEFetcher, DuckDuckGoFetcher, BingSearchFetcher, YandexSearchFetcher, MainFetcher, MultiSearchFetcher
from metadata.core.basic import save_to_json, save_to_yaml
from metadata.core.export_formats import save_to_docx, save_to_pdf, save_to_txt
from metadata.core.schema_formatter import SchemaFormatter
from utils.tool_normalizer import tool_normalizer

class MetadataFetcher:
    """Handles metadata fetching operations with improved logic."""
    
    def __init__(self):
        self.registry = None
        self.config = None
        
        # Define supported tools by category
        self.supported_tools = {
            'ai_ml': [
                'pytorch', 'tensorflow', 'anaconda', 'pandas', 
                'jupyter_lab', 'jupyter_notebook', 'langchain', 'ollama', 'hugging_face_transformers',
                'scikit-learn', 'numpy', 'matplotlib', 'seaborn', 'plotly'
            ],
            'data_science': [
                'pandas', 'jupyter_lab', 'jupyter_notebook', 'anaconda', 'numpy', 'matplotlib',
                'scikit-learn', 'seaborn', 'plotly', 'scipy', 'statsmodels'
            ],
            'creative_media': [
                'blender', 'gimp', 'elgato_stream_deck', 'comfy_ui', 'photoshop', 'illustrator'
            ],
            'developer_tools': [
                'visual_studio_code', 'git_version_control', 'pycharm', 'github_desktop', 'sublime', 'atom',
                'intellij', 'eclipse', 'vim', 'emacs'
            ],
            'llm_tools': [
                'langchain', 'ollama', 'hugging_face_transformers', 'openai', 'anthropic'
            ],
            'programming_languages': [
                'python', 'r', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin'
            ]
        }
        
        # Flatten the tool list for easy lookup
        self.all_supported_tools = []
        for tools in self.supported_tools.values():
            self.all_supported_tools.extend(tools)
    
    def setup_registry(self, output_format="json", output_directory="outputs"):
        """Setup the fetcher registry with configuration."""
        self.config = FetcherConfig(
            output_format=output_format,
            output_directory=output_directory
        )
        
        self.registry = FetcherRegistry(self.config)
        
        # Register MainFetcher first (highest priority for programming languages and online data)
        self.registry.register_class(MainFetcher)
        
        # Register MultiSearchFetcher for comprehensive search engine results
        self.registry.register_class(MultiSearchFetcher)
        
        # Register other online sources
        self.registry.register_class(GoogleCSEFetcher)
        self.registry.register_class(PyPIFetcher)
        self.registry.register_class(GitHubFetcher)
        self.registry.register_class(DockerHubFetcher)
        self.registry.register_class(DocsFetcher)
        
        # Register alternative search engines as fallbacks
        self.registry.register_class(DuckDuckGoFetcher)
        self.registry.register_class(BingSearchFetcher)
        self.registry.register_class(YandexSearchFetcher)
    
    def fetch_tool_metadata(self, tool_name, output_format="json", output_directory="outputs"):
        """Fetch metadata for a single tool with improved logic."""
        try:
            # Setup registry
            self.setup_registry(output_format, output_directory)
            
            # Normalize tool name
            original_tool_name = tool_name
            normalized_tool_name = tool_normalizer.normalize_tool_name(tool_name)
            display_name = tool_normalizer.get_display_name(tool_name)
            
            # Show what we're actually fetching
            if normalized_tool_name != original_tool_name.lower():
                click.echo(f"🔄 Normalized '{original_tool_name}' to '{normalized_tool_name}'")
                click.echo(f"📝 Display name: {display_name}")
            
            # Pre-validate tool name
            if not self._validate_tool_name(normalized_tool_name):
                click.echo(f"❌ Invalid tool name: {original_tool_name}")
                click.echo("💡 Try a valid tool name from our supported list:")
                self._show_supported_tools()
                return None
            
            # Fetch metadata with better error handling
            click.echo(f"🔄 Fetching metadata for: {display_name}")
            click.echo("🔍 Trying online sources first...")
            
            metadata = self.registry.fetch_metadata(normalized_tool_name)
            
            if not metadata:
                click.echo(f"❌ No metadata found for {display_name}")
                click.echo("💡 Try searching for a different tool name or check spelling")
                self._suggest_alternatives(normalized_tool_name)
                return None
            
            # Validate and improve metadata quality
            metadata = self._improve_metadata_quality(metadata, normalized_tool_name)
            
            # Update display name to use our standardized name
            metadata.display_name = display_name
            
            # Create output path using normalized name
            output_path = self.config.create_output_path(normalized_tool_name, output_format)
            
            # Export based on format
            self._export_metadata(metadata, output_path, output_format)
            
            click.echo(f"✅ Saved to: {output_path}")
            
            # Print summary without blank lines
            self._print_summary(metadata)
            
            return metadata
            
        except Exception as e:
            click.echo(f"❌ Error: {e}")
            click.echo("💡 Try a different tool name or check your internet connection")
            return None
    
    def _validate_tool_name(self, tool_name):
        """Validate if the tool name is reasonable."""
        if not tool_name or len(tool_name.strip()) == 0:
            return False
        
        # Check if it's a known tool with variations
        if tool_normalizer.is_known_tool(tool_name):
            return True
        
        # Check if it's in our supported tools list
        tool_name_lower = tool_name.lower()
        return tool_name_lower in self.all_supported_tools
    
    def _show_supported_tools(self):
        """Show supported tools by category."""
        click.echo("📋 Supported Tools by Category:")
        click.echo("AI/ML Development Tools:")
        click.echo(f"  {', '.join(self.supported_tools['ai_ml'])}")
        click.echo("Data Science and Analytics Tools:")
        click.echo(f"  {', '.join(self.supported_tools['data_science'])}")
        click.echo("Creative and Media Tools:")
        click.echo(f"  {', '.join(self.supported_tools['creative_media'])}")
        click.echo("Developer Tools:")
        click.echo(f"  {', '.join(self.supported_tools['developer_tools'])}")
        click.echo("Large Language Models (LLM) Tools:")
        click.echo(f"  {', '.join(self.supported_tools['llm_tools'])}")
        click.echo("Programming Languages (Fallback):")
        click.echo(f"  {', '.join(self.supported_tools['programming_languages'])}")
        
        # Show known tool variations
        click.echo("\n🔄 Tool Name Variations (you can use any of these):")
        for normalized_name in tool_normalizer.get_all_known_tools():
            display_name = tool_normalizer.get_display_name(normalized_name)
            aliases = tool_normalizer.get_aliases(normalized_name)
            click.echo(f"  {display_name}: {', '.join(aliases)}")
    
    def _suggest_alternatives(self, tool_name):
        """Suggest alternative tool names."""
        tool_name_lower = tool_name.lower()
        
        # Check if this tool has known variations
        if tool_normalizer.is_known_tool(tool_name):
            normalized_name = tool_normalizer.normalize_tool_name(tool_name)
            aliases = tool_normalizer.get_aliases(normalized_name)
            if aliases:
                click.echo(f"💡 Try these variations: {', '.join(aliases)}")
                return
        
        # Find similar tools
        suggestions = []
        for tool in self.all_supported_tools:
            if tool_name_lower in tool or tool in tool_name_lower:
                suggestions.append(tool)
        
        if suggestions:
            click.echo(f"💡 Did you mean one of these? {', '.join(suggestions[:5])}")
        else:
            click.echo("💡 Try one of our supported tools from the list above.")
    
    def _improve_metadata_quality(self, metadata, tool_name):
        """Improve metadata quality with fallbacks."""
        # If we don't have a good description, try to get one
        if not metadata.description or len(metadata.description.strip()) < 10:
            metadata.description = self._get_better_description(tool_name, metadata)
        
        # If we don't have installation methods, add a generic one
        if len(metadata.installation_methods) == 0:
            metadata.add_installation_method(
                method="generic",
                command=f"# Install {tool_name} using your package manager",
                description=f"Install {tool_name} using your system's package manager"
            )
        
        # If we don't have a version, try to get one
        if not metadata.version or metadata.version == 'None':
            metadata.version = self._get_version_info(tool_name, metadata)
        
        return metadata
    
    def _get_better_description(self, tool_name, metadata):
        """Try to get a better description from various sources."""
        # Try PyPI first
        try:
            response = requests.get(f"https://pypi.org/pypi/{tool_name}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                description = data.get('info', {}).get('summary', '')
                if description and len(description) > 10:
                    return description
        except:
            pass
        
        # Try GitHub search
        try:
            response = requests.get(
                f"https://api.github.com/search/repositories?q={tool_name}&sort=stars&order=desc&per_page=1",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    description = data['items'][0].get('description', '')
                    if description and len(description) > 10:
                        return description
        except:
            pass
        
        # Fallback description
        return f"Information about {tool_name} tool or package."
    
    def _get_version_info(self, tool_name, metadata):
        """Try to get version information."""
        # Try PyPI
        try:
            response = requests.get(f"https://pypi.org/pypi/{tool_name}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get('info', {}).get('version', '')
                if version:
                    return version
        except:
            pass
        
        return "Latest"
    
    def _export_metadata(self, metadata, output_path, output_format):
        """Export metadata to the specified format."""
        # Use SchemaFormatter for better formatting
        formatter = SchemaFormatter()
        
        if output_format == 'json':
            formatter.format_json(metadata, output_path)
        elif output_format == 'yaml':
            formatter.format_yaml(metadata, output_path)
        elif output_format == 'txt':
            formatter.format_txt(metadata, output_path)
        elif output_format == 'docx':
            formatter.format_docx(metadata, output_path)
        elif output_format == 'pdf':
            formatter.format_pdf(metadata, output_path)
    
    def _print_summary(self, metadata):
        """Print metadata summary without blank lines."""
        click.echo("📋 Summary:")
        click.echo(f"  Name: {metadata.name}")
        click.echo(f"  Display Name: {metadata.display_name}")
        click.echo(f"  Category: {metadata.category.value}")
        click.echo(f"  Description: {metadata.description}")
        click.echo(f"  Version: {metadata.version}")
        click.echo(f"  Installation Methods: {len(metadata.installation_methods)}")
        click.echo(f"  Sources: {metadata.sources}")
        click.echo(f"  Complete: {metadata.is_complete()}")
    
    def batch_fetch(self, tool_list, output_format="json", output_directory="outputs"):
        """Fetch metadata for multiple tools."""
        try:
            # Setup registry
            self.setup_registry(output_format, output_directory)
            
            # Process tools
            results = []
            click.echo(f"🔄 Processing {len(tool_list)} tools...")
            
            for i, tool_name in enumerate(tool_list, 1):
                try:
                    click.echo(f"[{i}/{len(tool_list)}] Fetching: {tool_name}")
                    metadata = self.registry.fetch_metadata(tool_name)
                    
                    if metadata:
                        # Create output path
                        output_path = self.config.create_output_path(tool_name, output_format)
                        
                        # Export
                        self._export_metadata(metadata, output_path, output_format)
                        
                        click.echo(f"✅ Saved to: {output_path}")
                        results.append((tool_name, True))
                    else:
                        click.echo(f"❌ No metadata found for {tool_name}")
                        results.append((tool_name, False))
                        
                except Exception as e:
                    click.echo(f"❌ Error processing {tool_name}: {e}")
                    results.append((tool_name, False))
            
            # Print batch summary
            self._print_batch_summary(results)
            
        except Exception as e:
            click.echo(f"❌ Error: {e}")
    
    def _print_batch_summary(self, results):
        """Print batch processing summary."""
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        click.echo("📊 Batch Summary:")
        click.echo(f"  Total tools: {total}")
        click.echo(f"  Successful: {successful}")
        click.echo(f"  Failed: {total - successful}")
        click.echo(f"  Success rate: {(successful/total*100):.1f}%") 