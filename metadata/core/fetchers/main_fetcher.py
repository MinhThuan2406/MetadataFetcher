"""
Enhanced Main Fetcher that combines hardcoded data with online search capabilities.
Handles programming languages and special tools with comprehensive data and online fallbacks.
"""

import requests
import time
import random
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, quote_plus
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MainFetcher(BaseFetcher):
    """
    Enhanced fetcher that combines hardcoded data with online search capabilities.
    Handles programming languages and special tools with comprehensive data.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "MainFetcher"
        
        # Load hardcoded data
        self.special_tools_data = self._load_data()
        
        # Multiple search engines and sources for online fallbacks
        self.search_engines = {
            'duckduckgo': 'https://api.duckduckgo.com/',
            'bing': 'https://api.bing.microsoft.com/v7.0/search',
            'yandex': 'https://yandex.com/search/xml'
        }
        
        # Tool-specific sources for online data
        self.tool_sources = {
            'python': [
                'https://www.python.org/doc/',
                'https://docs.python.org/3/',
                'https://pypi.org/project/python/',
                'https://github.com/python/cpython'
            ],
            'pandas': [
                'https://pandas.pydata.org/docs/',
                'https://pypi.org/project/pandas/',
                'https://github.com/pandas-dev/pandas'
            ],
            'tensorflow': [
                'https://www.tensorflow.org/',
                'https://pypi.org/project/tensorflow/',
                'https://github.com/tensorflow/tensorflow'
            ],
            'pytorch': [
                'https://pytorch.org/docs/',
                'https://pypi.org/project/torch/',
                'https://github.com/pytorch/pytorch'
            ],
            'visual_studio_code': [
                'https://code.visualstudio.com/docs/',
                'https://github.com/microsoft/vscode',
                'https://marketplace.visualstudio.com/'
            ],
            'git': [
                'https://git-scm.com/doc',
                'https://github.com/git/git',
                'https://git-scm.com/book/en/v2'
            ],
            'github': [
                'https://docs.github.com/',
                'https://github.com/github/docs',
                'https://help.github.com/'
            ],
            'docker': [
                'https://docs.docker.com/',
                'https://hub.docker.com/',
                'https://github.com/docker/docker-ce'
            ],
            'jupyter': [
                'https://jupyter.org/documentation',
                'https://jupyterlab.readthedocs.io/',
                'https://jupyter-notebook.readthedocs.io/'
            ],
            'anaconda': [
                'https://docs.anaconda.com/',
                'https://www.anaconda.com/',
                'https://github.com/Anaconda-Platform'
            ],
            'blender': [
                'https://docs.blender.org/',
                'https://www.blender.org/',
                'https://github.com/blender/blender'
            ],
            'gimp': [
                'https://docs.gimp.org/',
                'https://www.gimp.org/',
                'https://github.com/GNOME/gimp'
            ]
        }
        
        # Generic sources for unknown tools
        self.generic_sources = [
            'https://github.com/',
            'https://pypi.org/',
            'https://www.npmjs.com/',
            'https://crates.io/',
            'https://rubygems.org/',
            'https://packagist.org/',
            'https://www.nuget.org/',
            'https://mvnrepository.com/',
            'https://search.maven.org/',
            'https://hex.pm/',
            'https://cpan.org/',
            'https://metacpan.org/'
        ]
        
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """Load hardcoded data for special tools."""
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Load tool classification
        classification_file = project_root / "tool_classification.yaml"
        tool_classification = {}
        if classification_file.exists():
            with open(classification_file, 'r', encoding='utf-8') as f:
                tool_classification = yaml.safe_load(f)
        
        # Load tool descriptions
        descriptions_file = project_root / "tool_descriptions.yaml"
        tool_descriptions = {}
        if descriptions_file.exists():
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                tool_descriptions = yaml.safe_load(f)
        
        # Load schema
        schema_file = project_root / "schema.yaml"
        schema = {}
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
        
        # Define hardcoded data for programming languages and special tools
        special_data = {
            "python": {
                "tool_name": "Python",
                "overview_description": "Python is a high-level, general-purpose programming language that has become the dominant choice for artificial intelligence, machine learning, and data science applications in 2025. Created by Guido van Rossum and first released in 1991, Python emphasizes code readability through its design philosophy of significant indentation and clean syntax. As a dynamically typed and interpreted language, Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. Its extensive standard library, massive ecosystem of third-party packages, and active global community have made it the most popular programming language for AI/ML development.",
                "primary_use_cases": [
                    "Building and training neural networks with frameworks like PyTorch and TensorFlow",
                    "Developing machine learning models for classification, regression, and clustering",
                    "Creating recommendation systems for e-commerce and streaming platforms",
                    "Natural language processing and text analysis applications",
                    "Data cleaning, preprocessing, and transformation pipelines",
                    "Statistical analysis and hypothesis testing",
                    "Data visualization and exploratory data analysis",
                    "Big data processing and ETL operations",
                    "Computer vision and image processing applications",
                    "Healthcare data analysis and clinical research",
                    "Automated trading and financial modeling",
                    "Building REST APIs and web services for ML model deployment",
                    "Creating data-driven web applications",
                    "Developing microservices architectures"
                ],
                "supported_platforms_os": [
                    "Windows 10 and newer (officially supported)",
                    "macOS 10.15 (Catalina) and newer with Intel x86 and Apple Silicon (M1/M2) support",
                    "Universal support across all major Linux distributions (Ubuntu, Fedora, CentOS, Debian)",
                    "FreeBSD 10 and newer",
                    "Android and iOS (Tier 3 support)",
                    "WebAssembly (WASI) with Tier 2 support"
                ],
                "installation_setup": "Official Python.org installer - Download platform-specific installers from python.org with pip package manager and IDLE development environment. Package Managers - Windows: Microsoft Store, Chocolatey; macOS: Homebrew, MacPorts; Linux: System package managers (apt, yum, dnf, pacman). Development Environment Installers - Anaconda/Miniconda for data science workflows, Pyenv for managing multiple Python versions. Advanced Installation - Building from source code for custom configurations, Docker containers, cloud-based development environments.",
                "key_features": [
                    "Clean, readable syntax with significant indentation",
                    "Dynamic typing with optional type hints for better code documentation",
                    "Interactive interpreter (REPL) with enhanced features in Python 3.13+",
                    "Comprehensive error messages with colored tracebacks",
                    "Experimental free-threaded mode without Global Interpreter Lock (GIL) in Python 3.13+",
                    "Just-In-Time (JIT) compiler for improved performance",
                    "Enhanced interactive shell with multi-line editing and syntax highlighting",
                    "Memory optimizations and improved garbage collection",
                    "Extensive standard library covering common programming tasks",
                    "Simple package management with pip and virtual environments",
                    "Excellent debugging and profiling tools",
                    "Strong testing framework ecosystem",
                    "Native C/C++ extension capabilities for performance-critical code",
                    "Multiprocessing and asyncio support for concurrent programming",
                    "GPU acceleration support through libraries like NumPy and PyTorch",
                    "Memory-efficient data structures and iterators"
                ],
                "integration_with_other_tools": "Machine Learning Frameworks: PyTorch, TensorFlow, Keras for neural network development; Scikit-learn for classical machine learning algorithms; OpenCV for computer vision, NLTK/spaCy for NLP. Data Science Ecosystem: Pandas for data analysis, NumPy for numerical computing; Matplotlib, Seaborn, Plotly for data visualization; Dask, PySpark for distributed computing. Development Tools Integration: VS Code, PyCharm, Jupyter notebooks for development environments; Git integration with GitHub, GitLab workflows; AWS, Google Cloud, Azure ML integration. Database and Storage: SQLAlchemy, PyMongo for database connectivity; Support for CSV, JSON, Parquet, HDF5, and more; Requests library for REST API consumption, FastAPI for API development.",
                "documentation_tutorials": [
                    "Comprehensive Python 3.13+ documentation at docs.python.org",
                    "Official Python tutorial for programming fundamentals",
                    "Library reference and language specification",
                    "What's New guides for each Python version",
                    "Real Python tutorials and courses for practical Python skills",
                    "DataCamp courses focusing on data science and ML applications",
                    "Coursera and edX university courses for structured learning",
                    "Python.org community tutorials and guides",
                    "W3Schools Python tutorial for beginners",
                    "GeeksforGeeks comprehensive Python resources",
                    "YouTube channels and video tutorials for visual learners",
                    "Jupyter notebooks and interactive examples for hands-on practice",
                    "Machine learning specific tutorials with Real Python",
                    "Project-based learning through GitHub repositories"
                ],
                "community_support": "Python.org community forums and mailing lists. Official Python Discord server with 60,000+ active members. Python Software Foundation for governance and events. Stack Overflow with millions of Python-related questions and answers. Reddit communities (r/Python, r/learnpython) with 1.3+ million members. GitHub with thousands of open-source Python projects. PyLadies for diversity and inclusion with 196+ global chapters. Local Python user groups and meetups worldwide. LinkedIn Python Developer Community for professional networking. Real Python community for structured learning. Python Discord for real-time help and collaboration. Conference and events like PyCon for knowledge sharing.",
                "licensing": "Python Software Foundation License Version 2 (PSF License) - Compatible with commercial and proprietary applications, allows modification, distribution, and commercial use. More permissive than GPL, similar to BSD and MIT licenses with no copyleft requirements for derivative works. GPL-compatible since Python 2.1 and widely accepted in enterprise environments.",
                "latest_version_release_date": "Python 3.13.3 (April 2025) - Latest stable release with Python 3.13.2 (February 2025) major new features, monthly bug fix releases and security updates. Python 3.14 (October 2025) - Next major release in development with annual major releases and 5-year long-term support.",
                "example_projects_notebooks": [
                    "Machine learning tutorials with scikit-learn and pandas",
                    "Deep learning projects using PyTorch and TensorFlow",
                    "Data science workflows with real-world datasets",
                    "Awesome Python repository with curated libraries and tools",
                    "PyTorch official examples repository with neural network implementations",
                    "Real-world applications in computer vision, NLP, and data analysis",
                    "Beginner-friendly tutorials covering Python basics to advanced topics",
                    "Step-by-step project notebooks for hands-on learning",
                    "Industry-specific examples in healthcare, finance, and technology",
                    "University course materials and assignments",
                    "Coding challenge solutions and algorithm implementations",
                    "Open-source contributions and collaborative projects"
                ],
                "performance_considerations": "Use built-in functions and libraries optimized in C (NumPy, Pandas). Leverage appropriate data structures (sets vs lists, tuples vs lists). Implement caching and memoization for repeated computations. Utilize generator expressions for memory-efficient iteration. Python 3.11+ delivers 10-60% performance improvements. Python 3.13+ introduces experimental JIT compilation. Free-threaded mode removes GIL limitations for CPU-bound tasks. Optimized memory management and garbage collection. Profile code using cProfile and other profiling tools. Monitor memory usage and allocation patterns. Identify algorithmic complexity issues. Consider C extensions or Cython for performance-critical sections. Choose appropriate algorithms and data structures. Minimize global variable lookups and function call overhead. Use vectorized operations with NumPy for numerical computations. Consider async/await for I/O-bound applications.",
                "references_official_website_docs": [
                    "Official Website: https://www.python.org",
                    "Documentation: https://docs.python.org",
                    "Download Page: https://www.python.org/downloads/",
                    "Python Enhancement Proposals (PEPs): https://peps.python.org",
                    "Python Package Index (PyPI): https://pypi.org",
                    "GitHub Repository: https://github.com/python/cpython"
                ],
                "other_supporting_links_github": [
                    "https://docs.python.org/3/tutorial/ - Official Python Tutorial",
                    "https://realpython.com/ - Real Python Tutorials and Courses",
                    "https://www.python.org/downloads/ - Official Python Downloads",
                    "https://docs.python.org/3/whatsnew/ - What's New in Python Releases",
                    "https://packaging.python.org/ - Python Packaging User Guide",
                    "https://pypi.org/ - Python Package Index",
                    "https://github.com/vinta/awesome-python - Awesome Python Resources",
                    "https://docs.python.org/3/library/ - Python Standard Library Reference",
                    "https://www.python.org/community/ - Python Community Resources",
                    "https://discuss.python.org/ - Official Python Discussion Forum",
                    "https://stackoverflow.com/questions/tagged/python - Stack Overflow Python Questions",
                    "https://reddit.com/r/Python/ - Python Reddit Community",
                    "https://www.datacamp.com/courses/intro-to-python-for-data-science - DataCamp Python Course",
                    "https://jupyter.org/ - Project Jupyter for Interactive Development",
                    "https://code.visualstudio.com/docs/python/python-tutorial - VS Code Python Tutorial",
                    "https://www.coursera.org/courses?query=python - Coursera Python Courses",
                    "https://github.com/python/cpython - CPython Source Code Repository",
                    "https://peps.python.org/ - Python Enhancement Proposals",
                    "https://www.python.org/dev/peps/pep-0008/ - Python Style Guide (PEP 8)",
                    "https://wiki.python.org/moin/BeginnersGuide - Python Beginner's Guide"
                ],
                "dependencies": {
                    "latest": [
                        "No external dependencies required for basic Python installation",
                        "pip package manager included with Python 3.4+",
                        "setuptools for package development and distribution",
                        "wheel for binary package distribution",
                        "virtualenv or venv for environment isolation",
                        "Optional: NumPy, Pandas, Matplotlib for data science workflows",
                        "Optional: PyTorch, TensorFlow for machine learning",
                        "Optional: Django, Flask, FastAPI for web development"
                    ]
                },
                "system_requirements": "Operating System: Windows 10+, macOS 10.15+, Linux (various distributions). Memory: 512MB RAM minimum, 4GB+ recommended for data science. Storage: 100MB for basic installation, 1GB+ for full development environment. Processor: Any modern CPU (multi-core recommended for data processing). Network: Internet connection for package installation and updates. Display: Any modern display (higher resolution recommended for IDEs)."
            },
            "r": {
                "tool_name": "R",
                "overview_description": "R is a programming language and free software environment for statistical computing and graphics supported by the R Foundation for Statistical Computing. It is widely used among statisticians and data miners for developing statistical software and data analysis. R provides a wide variety of statistical and graphical techniques, and is highly extensible.",
                "primary_use_cases": [
                    "Statistical analysis and hypothesis testing",
                    "Data visualization and plotting",
                    "Machine learning and predictive modeling",
                    "Bioinformatics and computational biology",
                    "Financial analysis and econometrics",
                    "Social sciences research and surveys",
                    "Quality control and process improvement",
                    "Clinical trials and medical research",
                    "Environmental data analysis",
                    "Market research and consumer analytics"
                ],
                "supported_platforms_os": [
                    "Windows 10 and newer",
                    "macOS 10.13 (High Sierra) and newer",
                    "Linux (Ubuntu, Debian, CentOS, RHEL)",
                    "FreeBSD and other Unix-like systems"
                ],
                "installation_setup": "CRAN (Comprehensive R Archive Network) - Official R distribution. RStudio - Integrated development environment for R. Microsoft R Open - Enhanced R distribution with Intel MKL. Bioconductor - Bioinformatics packages for R. Package managers - conda, homebrew, apt, yum.",
                "key_features": [
                    "Comprehensive statistical analysis capabilities",
                    "Advanced data visualization with ggplot2",
                    "Extensive package ecosystem (CRAN, Bioconductor)",
                    "Reproducible research with R Markdown",
                    "Interactive data exploration tools",
                    "Machine learning with caret and other packages",
                    "Big data processing with dplyr and data.table",
                    "Time series analysis and forecasting",
                    "Spatial data analysis and mapping",
                    "Web application development with Shiny"
                ],
                "integration_with_other_tools": "Python integration via reticulate package. Database connectivity (SQL, NoSQL). Cloud computing platforms (AWS, Azure, Google Cloud). Version control with Git integration. Docker containers for reproducible environments. Jupyter notebooks via IRkernel. Apache Spark integration via sparklyr.",
                "documentation_tutorials": [
                    "Official R documentation at cran.r-project.org",
                    "RStudio tutorials and learning resources",
                    "R for Data Science online book",
                    "CRAN task views for domain-specific packages",
                    "R-bloggers community blog aggregator",
                    "Stack Overflow R tag for Q&A",
                    "YouTube channels dedicated to R tutorials",
                    "University courses and MOOCs",
                    "R User Groups and conferences",
                    "Package vignettes and examples"
                ],
                "community_support": "R Foundation for Statistical Computing. RStudio community and forums. Stack Overflow with 100,000+ R questions. R-bloggers community blog. R User Groups worldwide. CRAN package maintainers network. Bioconductor community for bioinformatics. Academic and research institutions. Professional conferences (useR!, RStudio Conf). GitHub repositories and open source projects.",
                "licensing": "GNU General Public License v2 - Free software license that ensures users have the freedom to use, study, share, and modify the software. Compatible with commercial use and widely adopted in academic and research environments.",
                "latest_version_release_date": "R 4.4.0 (April 2024) - Latest stable release with improved performance, new features for data manipulation, enhanced graphics capabilities, and updated statistical functions. Regular releases every 6 months with long-term support versions.",
                "example_projects_notebooks": [
                    "Statistical analysis workflows with real datasets",
                    "Data visualization projects using ggplot2",
                    "Machine learning tutorials with caret",
                    "Bioinformatics analysis with Bioconductor",
                    "Financial modeling and time series analysis",
                    "Reproducible research with R Markdown",
                    "Interactive dashboards with Shiny",
                    "Big data processing examples",
                    "Academic research and publication examples",
                    "Industry-specific case studies"
                ],
                "performance_considerations": "Use data.table for large dataset operations. Vectorize operations instead of loops. Leverage compiled code via Rcpp. Utilize parallel processing with parallel package. Profile code with Rprof and profvis. Optimize memory usage with gc(). Use appropriate data structures and classes. Consider Rcpp for performance-critical sections. Leverage cloud computing for big data. Use specialized packages for domain-specific tasks.",
                "references_official_website_docs": [
                    "Official Website: https://www.r-project.org",
                    "CRAN: https://cran.r-project.org",
                    "RStudio: https://www.rstudio.com",
                    "Bioconductor: https://bioconductor.org",
                    "R Foundation: https://www.r-project.org/foundation"
                ],
                "other_supporting_links_github": [
                    "https://cran.r-project.org/manuals.html - Official R Manuals",
                    "https://www.rstudio.com/resources/cheatsheets/ - RStudio Cheat Sheets",
                    "https://r4ds.had.co.nz/ - R for Data Science Book",
                    "https://ggplot2.tidyverse.org/ - ggplot2 Documentation",
                    "https://dplyr.tidyverse.org/ - dplyr Documentation",
                    "https://www.tidyverse.org/ - Tidyverse Ecosystem",
                    "https://shiny.rstudio.com/ - Shiny Web Applications",
                    "https://rmarkdown.rstudio.com/ - R Markdown",
                    "https://www.r-bloggers.com/ - R Bloggers Community",
                    "https://stackoverflow.com/questions/tagged/r - Stack Overflow R Questions"
                ],
                "dependencies": {
                    "latest": [
                        "R base installation from CRAN",
                        "RStudio IDE (recommended)",
                        "Essential packages: tidyverse, ggplot2, dplyr",
                        "Statistical packages: stats, MASS, car",
                        "Visualization packages: ggplot2, plotly, leaflet",
                        "Machine learning: caret, randomForest, e1071",
                        "Bioinformatics: Bioconductor packages",
                        "Development tools: devtools, roxygen2"
                    ]
                },
                "system_requirements": "Operating System: Windows 10+, macOS 10.13+, Linux. Memory: 4GB RAM minimum, 8GB+ recommended. Storage: 2GB for base installation, 10GB+ for full environment. Processor: Multi-core CPU recommended. Network: Internet connection for package installation. Display: High-resolution display for graphics."
            }
        }
        
        return special_data
    
    def can_fetch(self, tool_name: str) -> bool:
        """Check if this fetcher can handle the given tool."""
        # Handle programming languages and any tool that might have online data
        programming_languages = ["python", "r", "javascript", "java", "c++", "c#", "go", "rust", "swift", "kotlin", "php", "ruby", "perl", "scala", "haskell"]
        return tool_name.lower() in programming_languages or True  # Can handle any tool with online fallback
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata using hardcoded data first, then online sources as fallback."""
        try:
            tool_name_lower = tool_name.lower()
            
            # First, try hardcoded data for programming languages
            if tool_name_lower in self.special_tools_data:
                logger.info(f"MainFetcher: Using hardcoded data for {tool_name}")
                return self._fetch_from_hardcoded_data(tool_name)
            
            # If no hardcoded data, try online sources
            logger.info(f"MainFetcher: Searching online sources for {tool_name}")
            return self._fetch_from_online_sources(tool_name)
            
        except Exception as e:
            logger.error(f"MainFetcher: Error fetching {tool_name}: {e}")
            return None
    
    def _fetch_from_hardcoded_data(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata from hardcoded data."""
        try:
            tool_name_lower = tool_name.lower()
            data = self.special_tools_data[tool_name_lower]
            
            # Create UnifiedMetadata object
            metadata = UnifiedMetadata(
                name=tool_name,
                display_name=data.get("tool_name", tool_name.title()),
                description=data.get("overview_description", ""),
                category=ToolCategory.AI_ML,  # Default for programming languages
                source_priority="hardcoded"
            )
            
            # Add category-specific fields
            for field_name, value in data.items():
                if field_name not in ["tool_name", "overview_description"]:
                    metadata.set_field(field_name, value)
            
            # Add sources
            metadata.sources.append("main_fetcher")
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to fetch {tool_name} from hardcoded data: {e}")
            return None
    
    def _fetch_from_online_sources(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata from online sources."""
        try:
            # Try tool-specific sources first
            tool_specific_data = self._fetch_from_tool_specific_sources(tool_name)
            if tool_specific_data:
                logger.info(f"MainFetcher: Found tool-specific data for {tool_name}")
                return self._build_metadata_from_tool_specific_data(tool_name, tool_specific_data)
            
            # Try multiple search engines
            search_results = self._fetch_from_multiple_search_engines(tool_name)
            if search_results:
                logger.info(f"MainFetcher: Found search results for {tool_name}")
                return self._build_metadata_from_search_results(tool_name, search_results)
            
            # Try generic sources as last resort
            generic_data = self._fetch_from_generic_sources(tool_name)
            if generic_data:
                logger.info(f"MainFetcher: Found generic data for {tool_name}")
                return self._build_metadata_from_generic_data(tool_name, generic_data)
            
            logger.warning(f"MainFetcher: No data found for {tool_name}")
            return None
            
        except Exception as e:
            logger.error(f"MainFetcher: Error fetching online data for {tool_name}: {e}")
            return None
    
    def _fetch_from_tool_specific_sources(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Fetch data from tool-specific sources."""
        tool_name_lower = tool_name.lower()
        
        # Get tool-specific sources
        sources = self.tool_sources.get(tool_name_lower, [])
        if not sources:
            return None
        
        collected_data = {
            'descriptions': [],
            'features': [],
            'installation': [],
            'documentation': [],
            'links': []
        }
        
        for source in sources[:3]:  # Limit to 3 sources to avoid rate limiting
            try:
                data = self._fetch_from_single_source(tool_name, source)
                if data:
                    self._merge_collected_data(collected_data, data)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.debug(f"Error fetching from {source}: {e}")
                continue
        
        return collected_data if any(collected_data.values()) else None
    
    def _fetch_from_multiple_search_engines(self, tool_name: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch data from multiple search engines."""
        search_results = []
        
        # Try DuckDuckGo (no API key required)
        try:
            ddg_results = self._search_duckduckgo(tool_name)
            if ddg_results:
                search_results.extend(ddg_results)
        except Exception as e:
            logger.debug(f"DuckDuckGo search failed: {e}")
        
        # Try Bing (if API key available)
        try:
            bing_results = self._search_bing(tool_name)
            if bing_results:
                search_results.extend(bing_results)
        except Exception as e:
            logger.debug(f"Bing search failed: {e}")
        
        return search_results if search_results else None
    
    def _fetch_from_generic_sources(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Fetch data from generic sources as last resort."""
        collected_data = {
            'descriptions': [],
            'features': [],
            'installation': [],
            'documentation': [],
            'links': []
        }
        
        # Try a few generic sources
        for source in self.generic_sources[:5]:
            try:
                data = self._fetch_from_single_source(tool_name, source)
                if data:
                    self._merge_collected_data(collected_data, data)
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Error fetching from {source}: {e}")
                continue
        
        return collected_data if any(collected_data.values()) else None
    
    def _fetch_from_single_source(self, tool_name: str, source_url: str) -> Optional[Dict[str, Any]]:
        """Fetch data from a single source."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return self._parse_source_content(tool_name, response.text, source_url)
            
        except Exception as e:
            logger.debug(f"Error fetching from {source_url}: {e}")
        
        return None
    
    def _parse_source_content(self, tool_name: str, content: str, source_url: str) -> Dict[str, Any]:
        """Parse content from a source to extract relevant information."""
        import re
        
        # Remove HTML tags, scripts, and clean content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'&[a-zA-Z]+;', ' ', content)  # Remove HTML entities
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = re.sub(r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*\}', '', content)  # Remove JavaScript functions
        content = re.sub(r'const\s+\w+\s*=\s*[^;]+;', '', content)  # Remove JavaScript constants
        content = re.sub(r'var\s+\w+\s*=\s*[^;]+;', '', content)  # Remove JavaScript variables
        
        lines = content.split('\n')
        
        data = {
            'descriptions': [],
            'features': [],
            'installation': [],
            'documentation': [],
            'links': [{'url': source_url, 'title': f'{tool_name.title()} Documentation'}]
        }
        
        # Extract relevant information with better filtering
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            # Skip lines with too much technical content
            if any(skip in line.lower() for skip in ['function(', 'const ', 'var ', 'window.', 'document.', 'localStorage']):
                continue
                
            # Skip lines that are mostly URLs or technical code
            if re.search(r'https?://', line) and len(line) < 50:
                continue
                
            line_lower = line.lower()
            tool_name_lower = tool_name.lower()
            
            # Look for meaningful descriptions
            if tool_name_lower in line_lower:
                if len(line) > 30 and len(line) < 300:
                    # Check if it's a meaningful description
                    meaningful_words = ['editor', 'code', 'development', 'programming', 'tool', 'software', 'ide', 'debug', 'extension', 'visual studio']
                    if any(word in line_lower for word in meaningful_words):
                        data['descriptions'].append(line)
                        
            # Look for installation information
            if any(word in line_lower for word in ['install', 'download', 'setup', 'configure', 'download visual studio code']):
                if len(line) > 20 and len(line) < 200:
                    data['installation'].append(line)
                    
            # Look for features
            if any(word in line_lower for word in ['feature', 'capability', 'support', 'language', 'debug', 'extension', 'intellisense', 'git', 'terminal']):
                if len(line) > 20 and len(line) < 200:
                    data['features'].append(line)
                    
            # Look for documentation
            if any(word in line_lower for word in ['documentation', 'tutorial', 'guide', 'help', 'docs']):
                if len(line) > 20 and len(line) < 200:
                    data['documentation'].append(line)
        
        return data
    
    def _search_duckduckgo(self, tool_name: str) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API."""
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(tool_name)}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', tool_name.title()),
                        'snippet': data.get('Abstract', ''),
                        'link': data.get('AbstractURL', ''),
                        'source': 'duckduckgo'
                    })
                
                # Add related topics
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'link': topic.get('FirstURL', ''),
                            'source': 'duckduckgo'
                        })
                
                return results
                
        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")
        
        return []
    
    def _search_bing(self, tool_name: str) -> List[Dict[str, Any]]:
        """Search using Bing API (requires API key)."""
        # This would require a Bing API key
        # For now, return empty list
        return []
    
    def _merge_collected_data(self, collected: Dict[str, Any], new_data: Dict[str, Any]):
        """Merge new data into collected data."""
        for key in collected:
            if key in new_data and new_data[key]:
                collected[key].extend(new_data[key])
    
    def _build_metadata_from_tool_specific_data(self, tool_name: str, data: Dict[str, Any]) -> UnifiedMetadata:
        """Build metadata from tool-specific data."""
        category = self._determine_category(tool_name)
        
        # Create description from collected descriptions
        description = self._build_description_from_data(tool_name, data['descriptions'])
        
        metadata = UnifiedMetadata(
            name=tool_name,
            display_name=tool_name.title(),
            description=description,
            version="Latest",
            latest_version="Latest",
            category=category,
            source_priority="tool_specific"
        )
        
        # Add features (clean and limit)
        if data['features']:
            clean_features = []
            for feature in data['features'][:5]:
                # Clean up the feature text
                clean_feature = self._clean_text(feature)
                if clean_feature and len(clean_feature) > 10:
                    clean_features.append(clean_feature)
            if clean_features:
                metadata.set_field("key_features", clean_features)
        
        # Add installation info (clean and limit)
        if data['installation']:
            clean_installation = []
            for install in data['installation'][:3]:
                # Clean up the installation text
                clean_install = self._clean_text(install)
                if clean_install and len(clean_install) > 10:
                    clean_installation.append(clean_install)
            if clean_installation:
                metadata.set_field("installation_setup", clean_installation)
        
        # Add documentation
        if data['documentation']:
            clean_docs = []
            for doc in data['documentation'][:3]:
                clean_doc = self._clean_text(doc)
                if clean_doc and len(clean_doc) > 10:
                    clean_docs.append(clean_doc)
            if clean_docs:
                metadata.set_field("documentation_tutorials", clean_docs)
        
        # Add tool-specific fallback information if no data was found
        if tool_name.lower() == 'visual_studio_code':
            if not data['features']:
                metadata.set_field("key_features", [
                    "IntelliSense code completion and syntax highlighting",
                    "Built-in Git version control integration",
                    "Extensive extension marketplace",
                    "Integrated terminal and debugging tools",
                    "Multi-language support and custom themes"
                ])
            if not data['installation']:
                metadata.set_field("installation_setup", [
                    "Download Visual Studio Code from the official website",
                    "Install extensions from the marketplace for additional functionality",
                    "Configure settings and keyboard shortcuts for optimal workflow"
                ])
        
        # Add links
        for link in data['links']:
            metadata.add_link(
                url=link['url'],
                title=link['title'],
                link_type="documentation"
            )
        
        return metadata
    
    def _build_metadata_from_search_results(self, tool_name: str, results: List[Dict[str, Any]]) -> UnifiedMetadata:
        """Build metadata from search results."""
        category = self._determine_category(tool_name)
        
        # Extract descriptions from search results
        descriptions = [r.get('snippet', '') for r in results if r.get('snippet')]
        description = self._build_description_from_data(tool_name, descriptions)
        
        metadata = UnifiedMetadata(
            name=tool_name,
            display_name=tool_name.title(),
            description=description,
            version="Latest",
            latest_version="Latest",
            category=category,
            source_priority="search_results"
        )
        
        # Add links from search results
        for result in results:
            if result.get('link'):
                metadata.add_link(
                    url=result['link'],
                    title=result.get('title', tool_name.title()),
                    link_type="search_result"
                )
        
        return metadata
    
    def _build_metadata_from_generic_data(self, tool_name: str, data: Dict[str, Any]) -> UnifiedMetadata:
        """Build metadata from generic data (last resort)."""
        category = self._determine_category(tool_name)
        
        # Create a basic description
        description = f"{tool_name.title()} is a software tool or library used in software development and related fields."
        
        metadata = UnifiedMetadata(
            name=tool_name,
            display_name=tool_name.title(),
            description=description,
            version="Latest",
            latest_version="Latest",
            category=category,
            source_priority="generic"
        )
        
        # Add any collected data
        if data['features']:
            metadata.set_field("key_features", data['features'][:3])
        
        if data['installation']:
            metadata.set_field("installation_setup", data['installation'][:2])
        
        # Add links
        for link in data['links']:
            metadata.add_link(
                url=link['url'],
                title=link['title'],
                link_type="generic"
            )
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text for better readability."""
        import re
        
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common technical artifacts
        text = re.sub(r'//.*$', '', text)  # Remove comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # Remove block comments
        
        # Remove excessive punctuation
        text = re.sub(r'[;]{2,}', ';', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        # Clean up the text
        text = text.strip()
        
        # Ensure it's not too long
        if len(text) > 200:
            text = text[:200] + "..."
        
        return text
    
    def _build_description_from_data(self, tool_name: str, descriptions: List[str]) -> str:
        """Build a description from collected data."""
        if not descriptions:
            return f"{tool_name.title()} is a software tool used in development and related fields."
        
        # Clean and use the best description
        clean_descriptions = []
        for desc in descriptions:
            clean_desc = self._clean_text(desc)
            if clean_desc and len(clean_desc) > 20:
                clean_descriptions.append(clean_desc)
        
        if not clean_descriptions:
            return f"{tool_name.title()} is a software tool used in development and related fields."
        
        # Use the longest clean description
        best_description = max(clean_descriptions, key=len)
        
        # Ensure it's not too long
        if len(best_description) > 300:
            best_description = best_description[:300] + "..."
        
        return best_description
    
    def _determine_category(self, tool_name: str) -> ToolCategory:
        """Determine the category of a tool."""
        tool_name_lower = tool_name.lower()
        
        # Programming languages
        if tool_name_lower in ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin']:
            return ToolCategory.AI_ML
        
        # AI/ML tools
        if tool_name_lower in ['tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn']:
            return ToolCategory.AI_ML
        
        # Data science tools
        if tool_name_lower in ['jupyter', 'jupyterlab', 'matplotlib', 'seaborn']:
            return ToolCategory.DATA_SCIENCE
        
        # Developer tools
        if tool_name_lower in ['git', 'github', 'docker', 'visual_studio_code']:
            return ToolCategory.DEVELOPER_TOOLS
        
        # Creative tools
        if tool_name_lower in ['blender', 'gimp']:
            return ToolCategory.CREATIVE_MEDIA
        
        return ToolCategory.GENERIC
    
    def get_priority(self) -> int:
        return 2  # Medium priority to allow MultiSearchFetcher to run
    
    def get_supported_categories(self) -> list:
        return [ToolCategory.AI_ML, ToolCategory.DATA_SCIENCE, ToolCategory.DEVELOPER_TOOLS, ToolCategory.CREATIVE_MEDIA, ToolCategory.GENERIC] 