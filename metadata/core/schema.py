"""
Unified metadata schema for the refactored MetadataFetcher.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ToolCategory(Enum):
    """Tool categories for classification."""
    AI_ML = "ai_ml"
    CREATIVE_MEDIA = "creative_media"
    DATA_SCIENCE = "data_science"
    DEVELOPER_TOOLS = "developer_tools"
    LLM_TOOLS = "llm_tools"
    GENERIC = "generic"

@dataclass
class InstallationMethod:
    """Represents an installation method with metadata."""
    method: str  # e.g., "pip", "docker", "conda"
    command: str
    description: Optional[str] = None
    platform: Optional[str] = None  # e.g., "linux", "windows", "macos"
    requirements: Optional[List[str]] = None

@dataclass
class Link:
    """Represents a link with metadata."""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None  # e.g., "documentation", "homepage", "repository"

@dataclass
class UnifiedMetadata:
    """
    Unified metadata schema that consolidates all tool information.
    
    This schema replaces both PackageMetadata and ComprehensiveToolMetadata
    with a single, flexible structure that can handle any tool type.
    """
    
    # Core identification
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    latest_version: Optional[str] = None
    
    # Classification
    category: ToolCategory = ToolCategory.GENERIC
    tags: List[str] = field(default_factory=list)
    
    # Links and references
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    repository: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    
    # Installation information
    installation_methods: List[InstallationMethod] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    requirements: Optional[str] = None
    
    # Content
    readme_content: Optional[str] = None
    license: Optional[str] = None
    license_url: Optional[str] = None
    author: Optional[str] = None
    maintainer: Optional[str] = None
    
    # Category-specific fields (stored as key-value pairs)
    category_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Source tracking
    sources: List[str] = field(default_factory=list)  # e.g., ["pypi", "github", "web"]
    source_priority: str = "online"  # "online" or "fallback"
    last_updated: Optional[datetime] = None
    fetch_duration: Optional[float] = None  # seconds
    
    # Raw data for debugging/analysis
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.display_name is None:
            self.display_name = self.name.title()
        
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def add_link(self, url: str, title: Optional[str] = None, 
                 description: Optional[str] = None, link_type: Optional[str] = None):
        """Add a link to the metadata."""
        self.links.append(Link(url=url, title=title, description=description, type=link_type))
    
    def add_installation_method(self, method: str, command: str, 
                              description: Optional[str] = None, 
                              platform: Optional[str] = None,
                              requirements: Optional[List[str]] = None):
        """Add an installation method."""
        self.installation_methods.append(InstallationMethod(
            method=method,
            command=command,
            description=description,
            platform=platform,
            requirements=requirements
        ))
    
    def set_field(self, field_name: str, value: Any):
        """Set a category-specific field."""
        self.category_fields[field_name] = value
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Get a category-specific field."""
        return self.category_fields.get(field_name, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "latest_version": self.latest_version,
            "category": self.category.value,
            "tags": self.tags,
            "homepage": self.homepage,
            "documentation": self.documentation,
            "repository": self.repository,
            "links": [{"url": link.url, "title": link.title, 
                      "description": link.description, "type": link.type} 
                     for link in self.links],
            "installation_methods": [{"method": im.method, "command": im.command,
                                   "description": im.description, "platform": im.platform,
                                   "requirements": im.requirements} 
                                  for im in self.installation_methods],
            "dependencies": self.dependencies,
            "requirements": self.requirements,
            "readme_content": self.readme_content,
            "license": self.license,
            "license_url": self.license_url,
            "author": self.author,
            "maintainer": self.maintainer,
            "category_fields": self.category_fields,
            "sources": self.sources,
            "source_priority": self.source_priority,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "fetch_duration": self.fetch_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedMetadata':
        """Create from dictionary representation."""
        # Handle category enum
        category_str = data.get('category', 'generic')
        category = ToolCategory(category_str) if category_str else ToolCategory.GENERIC
        
        # Handle datetime
        last_updated = None
        if data.get('last_updated'):
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
            except ValueError:
                pass
        
        # Handle links
        links = []
        for link_data in data.get('links', []):
            links.append(Link(**link_data))
        
        # Handle installation methods
        installation_methods = []
        for im_data in data.get('installation_methods', []):
            installation_methods.append(InstallationMethod(**im_data))
        
        return cls(
            name=data['name'],
            display_name=data.get('display_name'),
            description=data.get('description'),
            version=data.get('version'),
            latest_version=data.get('latest_version'),
            category=category,
            tags=data.get('tags', []),
            homepage=data.get('homepage'),
            documentation=data.get('documentation'),
            repository=data.get('repository'),
            links=links,
            installation_methods=installation_methods,
            dependencies=data.get('dependencies', {}),
            requirements=data.get('requirements'),
            readme_content=data.get('readme_content'),
            license=data.get('license'),
            license_url=data.get('license_url'),
            author=data.get('author'),
            maintainer=data.get('maintainer'),
            category_fields=data.get('category_fields', {}),
            sources=data.get('sources', []),
            source_priority=data.get('source_priority', 'online'),
            last_updated=last_updated,
            fetch_duration=data.get('fetch_duration'),
            raw_data=data.get('raw_data', {})
        )
    
    def is_complete(self) -> bool:
        """Check if the metadata has essential information."""
        return bool(
            self.name and 
            (self.description or self.homepage or self.documentation)
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the metadata for quick overview."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category.value,
            "description": self.description,
            "version": self.version,
            "homepage": self.homepage,
            "documentation": self.documentation,
            "installation_methods_count": len(self.installation_methods),
            "sources": self.sources,
            "is_complete": self.is_complete()
        } 