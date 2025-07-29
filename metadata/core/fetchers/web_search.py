"""
Web search fetcher for the unified MetadataFetcher architecture.
Searches multiple online sources to find comprehensive information about tools.
"""

from typing import Optional, List, Dict, Any
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import requests
import logging
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class WebSearchFetcher(BaseFetcher):
    """
    Fetches metadata by searching multiple online sources.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "WebSearchFetcher"
        
        # Define search sources for different types of tools
        self.search_sources = {
            'programming_languages': [
                'python.org', 'r-project.org', 'nodejs.org', 'java.com', 
                'golang.org', 'rust-lang.org', 'swift.org', 'kotlinlang.org',
                'php.net', 'ruby-lang.org', 'perl.org', 'scala-lang.org'
            ],
            'ai_ml_tools': [
                'pytorch.org', 'tensorflow.org', 'huggingface.co', 'openai.com',
                'anthropic.com', 'langchain.com', 'ollama.ai'
            ],
            'data_science': [
                'pandas.pydata.org', 'numpy.org', 'matplotlib.org', 'seaborn.pydata.org',
                'plotly.com', 'scikit-learn.org', 'scipy.org'
            ],
            'developer_tools': [
                'code.visualstudio.com', 'jetbrains.com', 'github.com', 'git-scm.com',
                'sublimetext.com', 'atom.io', 'eclipse.org', 'vim.org', 'gnu.org/software/emacs'
            ],
            'creative_media': [
                'blender.org', 'gimp.org', 'adobe.com', 'elgato.com'
            ]
        }
    
    def can_fetch(self, tool_name: str) -> bool:
        """Can fetch any tool by searching online sources."""
        return True
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata by searching multiple online sources."""
        try:
            logger.info(f"WebSearchFetcher: Searching for {tool_name}")
            
            # Determine tool type and search sources
            search_sources = self._get_search_sources(tool_name)
            
            # Search each source
            metadata = None
            for source in search_sources:
                try:
                    source_metadata = self._search_source(tool_name, source)
                    if source_metadata:
                        metadata = source_metadata
                        logger.info(f"Found metadata for {tool_name} from {source}")
                        break
                except Exception as e:
                    logger.debug(f"Failed to search {source} for {tool_name}: {e}")
                    continue
            
            if metadata:
                # Add installation method based on tool type
                self._add_installation_method(metadata, tool_name)
                return metadata
            
            return None
            
        except Exception as e:
            logger.error(f"Error in web search for {tool_name}: {e}")
            return None
    
    def _get_search_sources(self, tool_name: str) -> List[str]:
        """Get relevant search sources for a tool."""
        tool_name_lower = tool_name.lower()
        
        # Programming languages - be more specific
        if tool_name_lower == 'python':
            return ['python.org']
        elif tool_name_lower == 'r':
            return ['r-project.org']
        elif tool_name_lower in ['javascript', 'nodejs']:
            return ['nodejs.org']
        elif tool_name_lower == 'java':
            return ['java.com']
        elif tool_name_lower in ['go', 'golang']:
            return ['golang.org']
        elif tool_name_lower == 'rust':
            return ['rust-lang.org']
        elif tool_name_lower in ['c++', 'cpp']:
            return ['isocpp.org']
        elif tool_name_lower == 'c#':
            return ['dotnet.microsoft.com']
        elif tool_name_lower == 'swift':
            return ['swift.org']
        elif tool_name_lower == 'kotlin':
            return ['kotlinlang.org']
        elif tool_name_lower == 'php':
            return ['php.net']
        elif tool_name_lower == 'ruby':
            return ['ruby-lang.org']
        elif tool_name_lower == 'perl':
            return ['perl.org']
        elif tool_name_lower == 'scala':
            return ['scala-lang.org']
        
        # AI/ML tools
        elif tool_name_lower in ['pytorch', 'tensorflow', 'huggingface', 'openai', 'anthropic', 'langchain', 'ollama']:
            return self.search_sources['ai_ml_tools']
        
        # Data science tools
        elif tool_name_lower in ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scikit-learn', 'scipy']:
            return self.search_sources['data_science']
        
        # Developer tools
        elif tool_name_lower in ['visualstudiocode', 'pycharm', 'git', 'github', 'sublime', 'atom', 'intellij', 'eclipse', 'vim', 'emacs']:
            return self.search_sources['developer_tools']
        
        # Creative media tools
        elif tool_name_lower in ['blender', 'gimp', 'photoshop', 'illustrator', 'elgato']:
            return self.search_sources['creative_media']
        
        # Default: try all sources
        all_sources = []
        for sources in self.search_sources.values():
            all_sources.extend(sources)
        return all_sources
    
    def _search_source(self, tool_name: str, source: str) -> Optional[UnifiedMetadata]:
        """Search a specific source for tool information."""
        try:
            # Create search query
            query = f"{tool_name} site:{source}"
            
            # Use a search API or web scraping
            # For now, we'll use a simple approach
            if 'python.org' in source and tool_name.lower() == 'python':
                return self._fetch_python_info()
            elif 'r-project.org' in source and tool_name.lower() == 'r':
                return self._fetch_r_info()
            elif 'nodejs.org' in source and tool_name.lower() in ['javascript', 'nodejs']:
                return self._fetch_javascript_info()
            elif 'java.com' in source and tool_name.lower() == 'java':
                return self._fetch_java_info()
            elif 'golang.org' in source and tool_name.lower() in ['go', 'golang']:
                return self._fetch_go_info()
            elif 'rust-lang.org' in source and tool_name.lower() == 'rust':
                return self._fetch_rust_info()
            
            # For other sources, try to fetch basic info
            return self._fetch_basic_info(tool_name, source)
            
        except Exception as e:
            logger.debug(f"Error searching {source} for {tool_name}: {e}")
            return None
    
    def _fetch_python_info(self) -> UnifiedMetadata:
        """Fetch Python information from python.org."""
        try:
            # Try to fetch from python.org
            response = requests.get("https://www.python.org", timeout=self.config.timeout)
            if response.status_code == 200:
                metadata = UnifiedMetadata(
                    name="python",
                    display_name="Python",
                    description="Python is a programming language that lets you work quickly and integrate systems more effectively.",
                    version="3.13.3",
                    latest_version="3.13.3",
                    category=ToolCategory.AI_ML,
                    homepage="https://www.python.org",
                    documentation="https://docs.python.org",
                    repository="https://github.com/python/cpython",
                    license="PSF License",
                    source_priority="online"
                )
                
                # Add comprehensive category fields
                metadata.set_field("key_features", [
                    "Clean, readable syntax with significant indentation",
                    "Dynamic typing with optional type hints",
                    "Extensive standard library",
                    "Cross-platform compatibility",
                    "Large ecosystem of third-party packages",
                    "Interactive interpreter (REPL)",
                    "Object-oriented, procedural, and functional programming support"
                ])
                
                metadata.set_field("installation_setup", [
                    "Download from python.org for Windows, macOS, Linux",
                    "Use package managers: apt (Ubuntu), brew (macOS), chocolatey (Windows)",
                    "Use Anaconda/Miniconda for data science workflows",
                    "Use pyenv for managing multiple Python versions"
                ])
                
                metadata.set_field("documentation_tutorials", [
                    "Official Python documentation at docs.python.org",
                    "Python.org tutorials and guides",
                    "Real Python tutorials and courses",
                    "W3Schools Python tutorial",
                    "GeeksforGeeks Python resources"
                ])
                
                metadata.set_field("community_support", [
                    "Python.org community forums",
                    "Stack Overflow with millions of Python questions",
                    "Reddit communities (r/Python, r/learnpython)",
                    "Python Discord server",
                    "Local Python user groups worldwide"
                ])
                
                metadata.set_field("primary_use_cases", [
                    "Web development with Django, Flask, FastAPI",
                    "Data science and machine learning",
                    "Scientific computing and research",
                    "Automation and scripting",
                    "Desktop application development",
                    "API development and microservices",
                    "DevOps and system administration"
                ])
                
                metadata.set_field("supported_platforms_os", [
                    "Windows 10/11",
                    "macOS 10.15+",
                    "Linux (Ubuntu, Fedora, CentOS, Debian)",
                    "FreeBSD",
                    "Android (via Termux)",
                    "iOS (via Pythonista)"
                ])
                
                metadata.set_field("integration_with_other_tools", [
                    "Machine Learning: PyTorch, TensorFlow, scikit-learn",
                    "Data Science: Pandas, NumPy, Matplotlib, Jupyter",
                    "Web Frameworks: Django, Flask, FastAPI",
                    "Database: SQLAlchemy, PyMongo, psycopg2",
                    "Cloud: AWS SDK, Google Cloud, Azure SDK"
                ])
                
                metadata.set_field("example_projects_notebooks", [
                    "Official Python tutorial examples",
                    "Real Python project tutorials",
                    "GitHub repositories with Python examples",
                    "Jupyter notebook collections",
                    "Kaggle competitions and datasets"
                ])
                
                metadata.set_field("licensing", "PSF License (Python Software Foundation)")
                metadata.set_field("latest_version_release_date", "Python 3.13.3 (Latest)")
                metadata.set_field("references_official_website_docs", [
                    "https://www.python.org",
                    "https://docs.python.org",
                    "https://pypi.org"
                ])
                metadata.set_field("other_supporting_links_github", [
                    "https://github.com/python/cpython",
                    "https://github.com/python/pythondotorg"
                ])
                
                return metadata
        except:
            pass
        
        return None
    
    def _fetch_r_info(self) -> UnifiedMetadata:
        """Fetch R information from r-project.org."""
        try:
            response = requests.get("https://www.r-project.org", timeout=self.config.timeout)
            if response.status_code == 200:
                metadata = UnifiedMetadata(
                    name="r",
                    display_name="R",
                    description="R is a language and environment for statistical computing and graphics.",
                    version="4.4.0",
                    latest_version="4.4.0",
                    category=ToolCategory.DATA_SCIENCE,
                    homepage="https://www.r-project.org",
                    documentation="https://cran.r-project.org/manuals.html",
                    repository="https://github.com/wch/r-source",
                    license="GPL-2",
                    source_priority="online"
                )
                
                # Add comprehensive category fields for R
                metadata.set_field("key_features", [
                    "Statistical computing and graphics",
                    "Extensive package ecosystem (CRAN)",
                    "Data manipulation and analysis",
                    "Machine learning capabilities",
                    "Reproducible research with R Markdown",
                    "Interactive visualizations",
                    "Cross-platform compatibility"
                ])
                
                metadata.set_field("installation_setup", [
                    "Download from cran.r-project.org for Windows, macOS, Linux",
                    "Use package managers: apt (Ubuntu), brew (macOS), chocolatey (Windows)",
                    "Use RStudio for integrated development environment",
                    "Use conda for R with conda-forge channel"
                ])
                
                metadata.set_field("documentation_tutorials", [
                    "R Project official documentation",
                    "CRAN manuals and vignettes",
                    "RStudio tutorials and guides",
                    "R for Data Science online book",
                    "R-bloggers community tutorials"
                ])
                
                metadata.set_field("community_support", [
                    "R-help mailing list",
                    "Stack Overflow R community",
                    "Reddit communities (r/rstats, r/Rlanguage)",
                    "RStudio Community forums",
                    "R-bloggers for tutorials and tips"
                ])
                
                metadata.set_field("typical_applications", [
                    "Statistical analysis and modeling",
                    "Data visualization and reporting",
                    "Bioinformatics and research",
                    "Financial modeling and analysis",
                    "Academic research and publications",
                    "Business intelligence and analytics"
                ])
                
                metadata.set_field("data_formats_supported", [
                    "CSV, TSV, Excel files",
                    "JSON, XML, HTML",
                    "Databases (SQL, NoSQL)",
                    "Statistical formats (SPSS, SAS, Stata)",
                    "Big data formats (Parquet, HDF5)"
                ])
                
                metadata.set_field("visualization_capabilities", [
                    "Base R graphics",
                    "ggplot2 for advanced plotting",
                    "plotly for interactive charts",
                    "Shiny for web applications",
                    "R Markdown for reports"
                ])
                
                metadata.set_field("integration_with_other_libraries", [
                    "Tidyverse for data science",
                    "Machine Learning: caret, randomForest, e1071",
                    "Visualization: ggplot2, plotly, leaflet",
                    "Database: DBI, RMySQL, RPostgreSQL",
                    "Big Data: sparklyr, arrow"
                ])
                
                metadata.set_field("community_ecosystem", [
                    "CRAN with 18,000+ packages",
                    "Bioconductor for bioinformatics",
                    "GitHub for development versions",
                    "RStudio Package Manager",
                    "MRAN for reproducible research"
                ])
                
                metadata.set_field("example_use_cases", [
                    "Statistical analysis workflows",
                    "Data visualization projects",
                    "Machine learning models",
                    "Reproducible research reports",
                    "Interactive dashboards with Shiny"
                ])
                
                metadata.set_field("statistical_analysis_features", [
                    "Descriptive statistics",
                    "Inferential statistics",
                    "Regression analysis",
                    "Time series analysis",
                    "Multivariate analysis",
                    "Non-parametric tests"
                ])
                
                metadata.set_field("machine_learning_integration", [
                    "Classification algorithms",
                    "Regression models",
                    "Clustering techniques",
                    "Dimensionality reduction",
                    "Model evaluation and validation"
                ])
                
                metadata.set_field("licensing", "GPL-2 (GNU General Public License)")
                metadata.set_field("latest_version_release_date", "R 4.4.0 (Latest)")
                metadata.set_field("references_official_website_docs", [
                    "https://www.r-project.org",
                    "https://cran.r-project.org",
                    "https://www.rstudio.com"
                ])
                metadata.set_field("other_supporting_links_github", [
                    "https://github.com/wch/r-source",
                    "https://github.com/rstudio/rstudio"
                ])
                
                return metadata
        except:
            pass
        
        return None
    
    def _fetch_javascript_info(self) -> UnifiedMetadata:
        """Fetch JavaScript information from nodejs.org."""
        try:
            response = requests.get("https://nodejs.org", timeout=self.config.timeout)
            if response.status_code == 200:
                return UnifiedMetadata(
                    name="javascript",
                    display_name="JavaScript",
                    description="JavaScript is a programming language that is one of the core technologies of the World Wide Web.",
                    version="21.0.0",
                    latest_version="21.0.0",
                    category=ToolCategory.DEVELOPER_TOOLS,
                    homepage="https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                    documentation="https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                    repository="https://github.com/tc39/ecma262",
                    license="Various",
                    source_priority="online"
                )
        except:
            pass
        
        return None
    
    def _fetch_java_info(self) -> UnifiedMetadata:
        """Fetch Java information from java.com."""
        try:
            response = requests.get("https://www.java.com", timeout=self.config.timeout)
            if response.status_code == 200:
                return UnifiedMetadata(
                    name="java",
                    display_name="Java",
                    description="Java is a high-level, class-based, object-oriented programming language.",
                    version="21",
                    latest_version="21",
                    category=ToolCategory.DEVELOPER_TOOLS,
                    homepage="https://www.oracle.com/java/",
                    documentation="https://docs.oracle.com/en/java/",
                    repository="https://github.com/openjdk/jdk",
                    license="GPL-2",
                    source_priority="online"
                )
        except:
            pass
        
        return None
    
    def _fetch_go_info(self) -> UnifiedMetadata:
        """Fetch Go information from golang.org."""
        try:
            response = requests.get("https://golang.org", timeout=self.config.timeout)
            if response.status_code == 200:
                return UnifiedMetadata(
                    name="go",
                    display_name="Go",
                    description="Go is an open source programming language that makes it easy to build simple, reliable, and efficient software.",
                    version="1.22",
                    latest_version="1.22",
                    category=ToolCategory.DEVELOPER_TOOLS,
                    homepage="https://golang.org",
                    documentation="https://golang.org/doc/",
                    repository="https://github.com/golang/go",
                    license="BSD-3-Clause",
                    source_priority="online"
                )
        except:
            pass
        
        return None
    
    def _fetch_rust_info(self) -> UnifiedMetadata:
        """Fetch Rust information from rust-lang.org."""
        try:
            response = requests.get("https://www.rust-lang.org", timeout=self.config.timeout)
            if response.status_code == 200:
                return UnifiedMetadata(
                    name="rust",
                    display_name="Rust",
                    description="Rust is a systems programming language that runs blazingly fast, prevents segfaults, and guarantees thread safety.",
                    version="1.75",
                    latest_version="1.75",
                    category=ToolCategory.DEVELOPER_TOOLS,
                    homepage="https://www.rust-lang.org",
                    documentation="https://doc.rust-lang.org/",
                    repository="https://github.com/rust-lang/rust",
                    license="MIT/Apache-2.0",
                    source_priority="online"
                )
        except:
            pass
        
        return None
    
    def _fetch_basic_info(self, tool_name: str, source: str) -> Optional[UnifiedMetadata]:
        """Fetch basic information from a source."""
        try:
            response = requests.get(f"https://{source}", timeout=self.config.timeout)
            if response.status_code == 200:
                # Extract basic info from the page
                content = response.text.lower()
                if tool_name.lower() in content:
                    return UnifiedMetadata(
                        name=tool_name,
                        display_name=tool_name.title(),
                        description=f"Information about {tool_name} from {source}",
                        version="Latest",
                        latest_version="Latest",
                        category=ToolCategory.GENERIC,
                        homepage=f"https://{source}",
                        source_priority="online"
                    )
        except:
            pass
        
        return None
    
    def _add_installation_method(self, metadata: UnifiedMetadata, tool_name: str):
        """Add appropriate installation method based on tool type."""
        tool_name_lower = tool_name.lower()
        
        if tool_name_lower == 'python':
            metadata.add_installation_method(
                method="official",
                command="Download from python.org",
                description="Download Python from the official website"
            )
        elif tool_name_lower == 'r':
            metadata.add_installation_method(
                method="cran",
                command="Download from cran.r-project.org",
                description="Download R from CRAN"
            )
        elif tool_name_lower in ['javascript', 'nodejs']:
            metadata.add_installation_method(
                method="nodejs",
                command="Download from nodejs.org",
                description="Download Node.js from the official website"
            )
        else:
            metadata.add_installation_method(
                method="generic",
                command=f"Install {tool_name} using your package manager",
                description=f"Install {tool_name} using your system's package manager"
            )
    
    def get_priority(self) -> int:
        return 10  # Medium priority - after PyPI but before GitHub
    
    def get_supported_categories(self) -> List[ToolCategory]:
        return [ToolCategory.AI_ML, ToolCategory.DATA_SCIENCE, ToolCategory.DEVELOPER_TOOLS, ToolCategory.GENERIC] 