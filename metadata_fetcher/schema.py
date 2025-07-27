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
    # --- New fields for richer metadata ---
    features: Optional[List[str]] = field(default_factory=list)  # Key features of the tool
    license: Optional[str] = None  # License type (e.g., MIT, BSD, GPL)
    license_url: Optional[str] = None  # URL to license text
    compatibility: Optional[List[str]] = field(default_factory=list)  # Compatible OS/platforms
    platforms: Optional[List[str]] = field(default_factory=list)  # Supported platforms (e.g., Windows, Linux, macOS)
    use_cases: Optional[List[str]] = field(default_factory=list)  # Typical use cases
    community_links: Optional[Dict[str, str]] = field(default_factory=dict)  # Community/support links (forum, chat, social)
    citation: Optional[str] = None  # Citation info or BibTeX
    benchmarks: Optional[List[str]] = field(default_factory=list)  # Benchmarks or performance links
    logo_url: Optional[str] = None  # URL to logo or image
    release_dates: Optional[Dict[str, str]] = field(default_factory=dict)  # Version -> release date
    project_status: Optional[str] = None  # Project status (active, maintenance, etc.)
    author: Optional[str] = None  # Author or maintainer
    maintainer: Optional[str] = None  # Maintainer
    changelog_url: Optional[str] = None  # Changelog or release notes URL
    api_reference_url: Optional[str] = None  # API reference URL
    tutorials_url: Optional[str] = None  # Tutorials or guides URL
    faq_url: Optional[str] = None  # FAQ URL
    contributing_url: Optional[str] = None  # Contributing guide URL
    code_of_conduct_url: Optional[str] = None  # Code of conduct URL
    development_status: Optional[str] = None  # Development status/classifier
    topics: Optional[List[str]] = field(default_factory=list)  # Tags or topics
    awards: Optional[List[str]] = field(default_factory=list)  # Awards or recognition
    integrations: Optional[List[str]] = field(default_factory=list)  # Integrations/plugins
    system_requirements: Optional[str] = None  # System requirements
    pricing: Optional[str] = None  # Pricing/cost info
    security: Optional[str] = None  # Security/privacy info
    roadmap_url: Optional[str] = None  # Roadmap/future plans URL
    known_issues_url: Optional[str] = None  # Known issues/limitations URL

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