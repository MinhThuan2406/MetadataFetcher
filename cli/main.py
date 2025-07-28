import click
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.core import FetcherRegistry, FetcherConfig, ToolCategory
from metadata.core.fetchers import PyPIFetcher, GitHubFetcher, DockerHubFetcher, DocsFetcher
from metadata.core.basic import save_to_json, save_to_yaml
from metadata.core.formats import save_to_docx, save_to_pdf, get_available_formats

@click.group()
def cli():
    """MetadataFetcher - Fetch tool metadata from multiple sources."""
    pass

@cli.command()
@click.argument('tool_name')
@click.option('--format', 'output_format', default='json', type=click.Choice(get_available_formats()), help='Output format')
@click.option('--output-dir', default='outputs', help='Output directory')
@click.option('--category', default=None, help='Tool category (optional)')
def fetch(tool_name, output_format, output_dir, category):
    """Fetch metadata for a single tool."""
    try:
        # Configure
        config = FetcherConfig(
            output_format=output_format,
            output_directory=output_dir
        )
        
        # Setup registry
        registry = FetcherRegistry(config)
        registry.register_class(PyPIFetcher)
        registry.register_class(GitHubFetcher)
        registry.register_class(DockerHubFetcher)
        registry.register_class(DocsFetcher)
        
        # Determine category if provided
        tool_category = None
        if category:
            try:
                tool_category = ToolCategory(category.lower())
            except ValueError:
                click.echo(f"Warning: Invalid category '{category}'. Using default.")
        
        # Fetch metadata
        click.echo(f"Fetching metadata for: {tool_name}")
        metadata = registry.fetch_metadata(tool_name, category=tool_category)
        
        if not metadata:
            click.echo(f"❌ No metadata found for {tool_name}")
            return
        
        # Create output path
        output_path = config.create_output_path(tool_name, output_format)
        
        # Export
        if output_format == 'json':
            save_to_json(metadata, output_path)
        elif output_format == 'yaml':
            save_to_yaml(metadata, output_path)
        elif output_format == 'docx':
            save_to_docx(metadata, output_path)
        elif output_format == 'pdf':
            save_to_pdf(metadata, output_path)
        
        click.echo(f"✅ Saved to: {output_path}")
        
        # Print summary
        click.echo(f"\nSummary:")
        click.echo(f"  name: {metadata.name}")
        click.echo(f"  display_name: {metadata.display_name}")
        click.echo(f"  category: {metadata.category.value}")
        click.echo(f"  description: {metadata.description}")
        click.echo(f"  version: {metadata.version}")
        click.echo(f"  homepage: {metadata.homepage}")
        click.echo(f"  documentation: {metadata.documentation}")
        click.echo(f"  installation_methods_count: {len(metadata.installation_methods)}")
        click.echo(f"  sources: {metadata.sources}")
        click.echo(f"  is_complete: {metadata.is_complete()}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input-file', type=click.Path(exists=True), help='File with tool names (one per line)')
@click.argument('tools', nargs=-1)
@click.option('--format', 'output_format', default='json', type=click.Choice(get_available_formats()), help='Output format')
@click.option('--output-dir', default='outputs', help='Output directory')
def batch(input_file, tools, output_format, output_dir):
    """Fetch metadata for multiple tools."""
    try:
        # Collect tool list
        tool_list = list(tools)
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_tools = [line.strip() for line in f if line.strip()]
                tool_list.extend(file_tools)
        
        if not tool_list:
            click.echo("❌ No tools specified. Use --input-file or provide tool names as arguments.")
            return
        
        # Configure
        config = FetcherConfig(
            output_format=output_format,
            output_directory=output_dir
        )
        
        # Setup registry
        registry = FetcherRegistry(config)
        registry.register_class(PyPIFetcher)
        registry.register_class(GitHubFetcher)
        registry.register_class(DockerHubFetcher)
        registry.register_class(DocsFetcher)
        
        # Process tools
        results = []
        click.echo(f"Processing {len(tool_list)} tools...")
        
        for i, tool_name in enumerate(tool_list, 1):
            try:
                click.echo(f"[{i}/{len(tool_list)}] Fetching: {tool_name}")
                metadata = registry.fetch_metadata(tool_name)
                
                if metadata:
                    # Create output path
                    output_path = config.create_output_path(tool_name, output_format)
                    
                    # Export
                    if output_format == 'json':
                        save_to_json(metadata, output_path)
                    elif output_format == 'yaml':
                        save_to_yaml(metadata, output_path)
                    elif output_format == 'docx':
                        save_to_docx(metadata, output_path)
                    elif output_format == 'pdf':
                        save_to_pdf(metadata, output_path)
                    
                    click.echo(f"✅ Saved to: {output_path}")
                    results.append((tool_name, True))
                else:
                    click.echo(f"❌ No metadata found for {tool_name}")
                    results.append((tool_name, False))
                    
            except Exception as e:
                click.echo(f"❌ Error processing {tool_name}: {e}")
                results.append((tool_name, False))
        
        # Summary
        successful = sum(1 for _, success in results if success)
        click.echo(f"\n📊 Batch Summary:")
        click.echo(f"  Total tools: {len(tool_list)}")
        click.echo(f"  Successful: {successful}")
        click.echo(f"  Failed: {len(tool_list) - successful}")
        click.echo(f"  Success rate: {(successful/len(tool_list)*100):.1f}%")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)

@cli.command()
def formats():
    """Show available output formats."""
    available_formats = get_available_formats()
    click.echo("Available output formats:")
    for fmt in available_formats:
        click.echo(f"  - {fmt}")

@cli.command()
def info():
    """Show system information."""
    click.echo("MetadataFetcher System Information:")
    click.echo(f"  Python version: {sys.version}")
    click.echo(f"  Available formats: {', '.join(get_available_formats())}")
    click.echo(f"  Default output directory: outputs/")
    click.echo(f"  Supported fetchers: PyPI, GitHub, DockerHub, Docs")

if __name__ == '__main__':
    cli() 