"""
Unified configuration for the MetadataFetcher system.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FetcherConfig:
    # Essential API Configuration
    google_api_keys: List[str] = field(default_factory=list)
    google_cse_id: Optional[str] = None
    github_token: Optional[str] = None
    
    # Request Settings
    request_delay: float = 1.0
    max_retries: int = 3
    timeout: float = 10.0
    
    # Output Settings
    output_format: str = "json"
    output_directory: str = "outputs"
    include_raw_data: bool = False
    
    # Caching
    enable_caching: bool = True
    cache_ttl: int = 86400
    cache_directory: str = "cache"
    
    # Logging
    log_level: str = "INFO"
    enable_console_logging: bool = True

    def __post_init__(self):
        # Load from environment variables
        if not self.google_api_keys:
            google_keys = os.getenv('GOOGLE_API_KEYS', '')
            if google_keys:
                self.google_api_keys = [key.strip() for key in google_keys.split(',')]
        
        if not self.google_cse_id:
            self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        
        if not self.github_token:
            self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Create output directories
        self._ensure_output_directories()
    
    def _ensure_output_directories(self):
        """Ensure output directories exist."""
        formats = ['json', 'yaml', 'docs', 'pdf']
        for format_type in formats:
            format_dir = os.path.join(self.output_directory, format_type)
            os.makedirs(format_dir, exist_ok=True)
    
    def create_output_path(self, tool_name: str, format_override: Optional[str] = None) -> str:
        """Create output file path with unified structure."""
        
        # Determine format
        output_format = format_override or self.output_format
        
        # Create filename without timestamp
        filename = f"{tool_name}.{output_format}"
        
        # Ensure output directory exists
        format_dir = os.path.join(self.output_directory, output_format)
        os.makedirs(format_dir, exist_ok=True)
        
        # Create full path
        output_path = os.path.join(format_dir, filename)
        
        return output_path
    
    def get_output_directory(self, format_type: str) -> str:
        """Get output directory for specific format."""
        return os.path.join(self.output_directory, format_type)
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Check output directory
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except Exception:
                return False
        
        # Check cache directory
        if self.enable_caching:
            try:
                os.makedirs(self.cache_directory, exist_ok=True)
            except Exception:
                return False
        
        return True 