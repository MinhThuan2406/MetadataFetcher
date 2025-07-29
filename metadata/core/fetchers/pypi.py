"""
PyPI fetcher for the unified MetadataFetcher architecture.
"""

from typing import Optional, List
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
import logging

logger = logging.getLogger(__name__)

class PyPIFetcher(BaseFetcher):
    """
    Fetches metadata for Python packages from PyPI.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "PyPIFetcher"
    
    def can_fetch(self, tool_name: str) -> bool:
        # Heuristic: PyPI fetcher is for Python packages (not for generic tools)
        # You may want to improve this with a real check
        return tool_name.lower() not in [
            'git', 'blender', 'gimp', 'comfyui', 'elgatostreamdeck', 'githubdesktop', 'pycharm', 'visualstudiocode', 'r'
        ]
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata from PyPI."""
        try:
            # Check cache first
            cached_metadata = self._get_cached_metadata(tool_name)
            if cached_metadata:
                logger.info(f"Using cached metadata for {tool_name}")
                return cached_metadata
            
            # Make API request
            url = f"https://pypi.org/pypi/{tool_name}/json"
            response = requests.get(url, timeout=self.config.timeout)
            
            if response.status_code == 404:
                logger.warning(f"PyPI: {tool_name} not found (status 404)")
                return None
            
            if response.status_code != 200:
                logger.warning(f"PyPI: {tool_name} request failed (status {response.status_code})")
                return None
            
            data = response.json()
            
            # Ensure data has the expected structure
            if not data or 'info' not in data:
                logger.warning(f"PyPI: Invalid response structure for {tool_name}")
                return None
            
            info = data['info']
            
            # Build metadata
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=info.get('name', tool_name),
                description=info.get('summary', ''),
                version=info.get('version', ''),
                latest_version=info.get('version', ''),
                category=ToolCategory.AI_ML,  # Default for Python packages
                homepage=info.get('home_page'),
                documentation=info.get('docs_url'),
                repository=info.get('project_urls', {}).get('Repository') if info.get('project_urls') else None,
                license=info.get('license'),
                author=info.get('author'),
                maintainer=info.get('maintainer'),
                source_priority="online"
            )
            
            # Add installation method
            metadata.add_installation_method(
                method="pip",
                command=f"pip install {tool_name}",
                description=f"Install {tool_name} using pip"
            )
            
            # Add dependencies
            if 'requires_dist' in info:
                # requires_dist can be None or a list of dependency strings
                if info['requires_dist'] is not None:
                    if isinstance(info['requires_dist'], list):
                        metadata.dependencies['latest'] = info['requires_dist']
                    else:
                        # If it's a string, split it into a list
                        metadata.dependencies['latest'] = [info['requires_dist']]
                else:
                    metadata.dependencies['latest'] = []
            
            # Add comprehensive category fields
            try:
                self._add_comprehensive_fields(metadata, tool_name, info)
                logger.info(f"Added comprehensive fields for {tool_name}")
            except Exception as e:
                logger.error(f"Error adding comprehensive fields for {tool_name}: {e}")
            
            # Cache the result
            self._cache_metadata(tool_name, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error fetching {tool_name} from PyPI: {e}")
            return None
    
    def get_priority(self) -> int:
        return 5  # High priority for PyPI
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.AI_ML, ToolCategory.DATA_SCIENCE, ToolCategory.GENERIC]
    
    def _add_comprehensive_fields(self, metadata: UnifiedMetadata, tool_name: str, info: dict):
        """Add comprehensive category fields based on package information."""
        
        # Add key features based on package type
        if tool_name.lower() in ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly']:
            metadata.set_field("key_features", [
                "Data manipulation and analysis",
                "Statistical computing capabilities",
                "Data visualization tools",
                "Integration with scientific Python ecosystem",
                "High-performance numerical computing",
                "Cross-platform compatibility"
            ])
            
            metadata.set_field("primary_use_cases", [
                "Data science and analytics",
                "Scientific computing and research",
                "Machine learning workflows",
                "Data visualization and reporting",
                "Statistical analysis",
                "Business intelligence"
            ])
            
            metadata.set_field("supported_platforms_os", [
                "Windows 10/11",
                "macOS 10.15+",
                "Linux (Ubuntu, Fedora, CentOS, Debian)",
                "Cross-platform Python compatibility"
            ])
            
            metadata.set_field("integration_with_other_tools", [
                "Jupyter notebooks and JupyterLab",
                "scikit-learn for machine learning",
                "SciPy for scientific computing",
                "NumPy for numerical operations",
                "Matplotlib for plotting",
                "Cloud platforms (AWS, GCP, Azure)"
            ])
            
            metadata.set_field("example_projects_notebooks", [
                "Official documentation examples",
                "GitHub repository tutorials",
                "Jupyter notebook collections",
                "Kaggle competitions and datasets",
                "Real-world data analysis projects"
            ])
            
        elif tool_name.lower() in ['tensorflow', 'pytorch', 'torch', 'keras']:
            metadata.set_field("key_features", [
                "Deep learning and neural networks",
                "GPU acceleration support",
                "Automatic differentiation",
                "Model training and inference",
                "Tensor operations and computations",
                "Production deployment capabilities"
            ])
            
            metadata.set_field("primary_use_cases", [
                "Deep learning model development",
                "Computer vision applications",
                "Natural language processing",
                "Neural network training",
                "Model deployment and serving",
                "Research and experimentation"
            ])
            
            metadata.set_field("model_types_supported", [
                "Convolutional Neural Networks (CNN)",
                "Recurrent Neural Networks (RNN)",
                "Transformer models",
                "Generative Adversarial Networks (GAN)",
                "Autoencoders and variational models"
            ])
            
            metadata.set_field("training_inference_capabilities", [
                "Distributed training across multiple GPUs",
                "Mixed precision training",
                "Model checkpointing and saving",
                "Real-time inference optimization",
                "Model quantization and optimization"
            ])
            
            metadata.set_field("hardware_acceleration_support", [
                "NVIDIA GPU acceleration with CUDA",
                "AMD GPU support with ROCm",
                "Apple Silicon (M1/M2) optimization",
                "TPU support for Google Cloud",
                "CPU optimization with Intel MKL"
            ])
            
        else:
            # Generic fields for other packages
            metadata.set_field("key_features", [
                "Python package ecosystem integration",
                "Cross-platform compatibility",
                "Extensive documentation",
                "Active community support",
                "Regular updates and maintenance"
            ])
            
            metadata.set_field("primary_use_cases", [
                "Python application development",
                "Library and framework usage",
                "Tool integration and automation",
                "Development and testing"
            ])
        
        # Common fields for all packages
        metadata.set_field("installation_setup", [
            f"pip install {tool_name}",
            f"conda install {tool_name} (if available)",
            "Use virtual environments for isolation",
            "Check system requirements and dependencies"
        ])
        
        metadata.set_field("documentation_tutorials", [
            f"PyPI package page: https://pypi.org/project/{tool_name}/",
            "Official documentation (if available)",
            "GitHub repository (if available)",
            "Community tutorials and examples"
        ])
        
        metadata.set_field("community_support", [
            "PyPI package community",
            "GitHub issues and discussions",
            "Stack Overflow questions and answers",
            "Python community forums",
            "Package-specific mailing lists"
        ])
        
        metadata.set_field("licensing", info.get('license', 'Unknown'))
        metadata.set_field("latest_version_release_date", f"{tool_name} {info.get('version', 'Latest')}")
        
        # Add links
        if info.get('home_page'):
            metadata.set_field("references_official_website_docs", [info['home_page']])
        if info.get('project_urls', {}).get('Repository'):
            metadata.set_field("other_supporting_links_github", [info['project_urls']['Repository']]) 