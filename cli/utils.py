"""
CLI utility functions.
"""

import click
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.core.export_formats import get_available_formats

def show_system_info():
    """Show system information."""
    click.echo("MetadataFetcher System Information:")
    click.echo(f"  Python version: {sys.version}")
    click.echo(f"  Available formats: {', '.join(get_available_formats())}")
    click.echo(f"  Default output directory: outputs/")
    click.echo(f"  Supported fetchers: PyPI, GitHub, DockerHub, Docs")

def show_formats():
    """Show available output formats."""
    click.echo("\n📋 Available Output Formats")
    click.echo("-" * 30)
    available_formats = get_available_formats()
    for fmt in available_formats:
        click.echo(f"  - {fmt}")

def get_format_from_choice(choice):
    """Convert numeric choice to format string."""
    format_map = {
        1: 'json',
        2: 'yaml',
        3: 'txt',
        4: 'docx',
        5: 'pdf'
    }
    
    if choice not in format_map:
        click.echo("❌ Invalid choice. Using JSON format.")
        return 'json'
    
    return format_map[choice]

def prompt_for_tool_name():
    """Prompt user for tool name."""
    return click.prompt("Enter tool name")

def prompt_for_format():
    """Prompt user for format choice."""
    click.echo("Choose output format:")
    click.echo("1. JSON")
    click.echo("2. YAML") 
    click.echo("3. TXT")
    click.echo("4. DOCX")
    click.echo("5. PDF")
    
    choice = click.prompt("Enter your choice (1-5)", type=int, default=1)
    return get_format_from_choice(choice)

def validate_format(format_name):
    """Validate if the format is supported."""
    available_formats = get_available_formats()
    if format_name not in available_formats:
        click.echo(f"❌ Invalid format '{format_name}'. Available formats: {', '.join(available_formats)}")
        return False
    return True 