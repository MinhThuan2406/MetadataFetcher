import click
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.fetcher import MetadataFetcher
from cli.utils import prompt_for_tool_name, prompt_for_format, show_system_info

@click.group()
def cli():
    """MetadataFetcher - Fetch tool metadata from multiple sources."""
    pass

@cli.command()
def fetch():
    """Simple fetch: Enter tool name and choose format."""
    try:
        # Step 1: Prompt for tool name
        tool_name = prompt_for_tool_name()
        
        # Step 2: Prompt for format choice
        output_format = prompt_for_format()
        
        # Create unified fetcher and fetch metadata
        fetcher = MetadataFetcher()
        fetcher.fetch_tool_metadata(tool_name, output_format, "outputs")
        
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye!")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)

@cli.command()
def info():
    """Show system information."""
    show_system_info()

if __name__ == '__main__':
    cli() 