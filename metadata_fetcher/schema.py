from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class InstallCommand:
    command: str
    explanation: Optional[str] = None
    note: Optional[str] = None
    when_to_use: Optional[str] = None

@dataclass
class InstallationInfo:
    pip: Optional[List[Dict[str, str]]] = field(default_factory=list)
    from_source: Optional[List[Dict[str, str]]] = field(default_factory=list)
    docker: Optional[List[Dict[str, str]]] = field(default_factory=list)
    docker_compose: Optional[List[Dict[str, str]]] = field(default_factory=list)
    other: Optional[List[Dict[str, str]]] = field(default_factory=list)
    platforms: Optional[Dict[str, List[Dict[str, str]]]] = field(default_factory=dict)

@dataclass
class PackageMetadata:
    name: str
    description: Optional[str] = None
    latest_version: Optional[str] = None
    popular_versions: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    github_url: Optional[str] = None
    readme_content: Optional[str] = None
    requirements: Optional[str] = None
    installation: InstallationInfo = field(default_factory=InstallationInfo)
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    source: Optional[str] = None
    homepage_html: Optional[str] = None
    documentation_html: Optional[str] = None
    documentation_links: List[str] = field(default_factory=list)
    installation_links: List[str] = field(default_factory=list)
    use_case: Optional[str] = None

"""
PackageMetadata schema:
- name: Name of the package/tool
- description: Short description
- latest_version: Latest version (from PyPI or GitHub)
- popular_versions: List of popular versions
- dependencies: Dict of version -> list of dependencies
- github_url: GitHub repository URL (if any)
- readme_content: Content of the README file (if any)
- requirements: Content of requirements.txt (if any)
- installation: InstallationInfo object with pip, from_source, docker, docker_compose, other, platforms
- homepage: Official homepage URL
- documentation: Documentation/setup guide URL (if found)
- source: 'pypi' or 'manual + google' (data origin)
- homepage_html: Raw HTML/text of the homepage (if fetched)
- documentation_html: Raw HTML/text of the documentation page (if fetched)
- documentation_links: List of all discovered documentation/setup links
- installation_links: List of all discovered installation-related links
"""

# Expanded metadata schema for creative/media tools
CREATIVE_MEDIA_SCHEMA = {
    'Name': str,
    'Type': str,
    'Description': str,
    'Official Site': str,
    'Versions': str,
    'Compatibility': str,
    'Key Features': str,
    'Installation & Documentation': str,
    'Support/Reviews': str,
    'License': str,  # e.g., GPL, MIT, proprietary
    'Latest Release Date': str,  # e.g., '2024-05-01'
    'Programming Language': str,  # e.g., 'C++', 'Python'
    'Supported File Formats': str,  # e.g., '.blend, .obj, .fbx'
    'System Requirements': str,  # e.g., 'Windows 10+, 8GB RAM, GPU'
    'Integrations/Plugins': str,  # e.g., 'Unity, Unreal, Adobe Suite'
    'Community & Ecosystem': str,  # e.g., forum links, Discord, Stack Overflow
    'Awards/Recognition': str,  # e.g., 'Academy Award for Technical Achievement'
    'Pricing/Cost': str,  # e.g., 'Free, Commercial licenses available'
    'Security/Privacy': str,  # e.g., 'GDPR compliant, sandboxed'
    'Roadmap/Future Plans': str,  # e.g., roadmap link or summary
    'Known Issues/Limitations': str,  # e.g., 'No native Apple Silicon support'
} 