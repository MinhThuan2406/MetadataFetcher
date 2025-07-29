"""
Special fetcher for programming languages and other tools that need hardcoded data.
"""

from typing import Optional, Dict, Any
from ..base import BaseFetcher
from ..schema import UnifiedMetadata, ToolCategory
from ..config import FetcherConfig
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MainFetcher(BaseFetcher):
    """
    Fetches metadata for programming languages and special tools using hardcoded data.
    """
    
    def __init__(self, config: Optional[FetcherConfig] = None):
        super().__init__(config)
        self.name = "MainFetcher"
        
        # Load hardcoded data
        self.special_tools_data = self._load_data()
        
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
        # Only handle programming languages that are not well-represented online
        # These are languages, not packages, so they won't be found on PyPI
        programming_languages = ["python", "r", "javascript", "java", "c++", "c#", "go", "rust", "swift", "kotlin", "php", "ruby", "perl", "scala", "haskell"]
        return tool_name.lower() in programming_languages
    
    def fetch(self, tool_name: str) -> Optional[UnifiedMetadata]:
        """Fetch metadata for a special tool using hardcoded data."""
        try:
            tool_name_lower = tool_name.lower()
            
            if tool_name_lower not in self.special_tools_data:
                return None
            
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
            metadata.sources.append("special_fetcher")
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to fetch {tool_name} from special fetcher: {e}")
            return None
    
    def get_priority(self) -> int:
        return 1  # Highest priority for programming languages with comprehensive data
    
    def get_supported_categories(self) -> list:
        return [ToolCategory.AI_ML, ToolCategory.DATA_SCIENCE, ToolCategory.DEVELOPER_TOOLS] 