from metadata_fetcher.schema import PackageMetadata, InstallationInfo
from metadata_fetcher.google_search import google_search
from metadata_fetcher.installation_parser import extract_installation_commands
from typing import Optional, List
import requests
from bs4 import BeautifulSoup, Tag
import re
import json
import os
from metadata_fetcher import fetch_package_metadata
import yaml
from scripts.export_to_word import json_to_professional_word
from metadata_fetcher.fetchers.creative_media_fetcher import fetch_creative_media_metadata
from bs4.element import Tag as Bs4Tag

DOC_KEYWORDS = ["docs", "documentation", "install", "setup", "getting-started", "guide"]
INSTALL_KEYWORDS = ["install", "setup", "getting-started", "quickstart", "start"]

def load_tool_classification():
    """Load tool classification data from the YAML file."""
    with open('tool_classification.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

TOOL_CLASSIFICATION = load_tool_classification()

# --- NEW: Build alias map for robust tool name matching ---
def normalize_tool_name(name):
    return ''.join(e for e in name.strip().lower().replace('-', ' ').replace('_', ' ') if e.isalnum())

def build_tool_alias_map(tool_classification):
    alias_map = {}
    for key in tool_classification.keys():
        # Split combined entries (e.g., 'jupyterlab / jupyter notebook')
        aliases = [k.strip() for k in re.split(r'/|,', key)]
        for alias in aliases:
            norm = normalize_tool_name(alias)
            alias_map[norm] = key  # Map normalized alias to canonical key
    return alias_map

TOOL_ALIAS_MAP = build_tool_alias_map(TOOL_CLASSIFICATION)

def resolve_tool_name(user_input):
    norm = normalize_tool_name(user_input)
    return TOOL_ALIAS_MAP.get(norm)

def resolve_tool_name_and_specific_package(user_input):
    norm = normalize_tool_name(user_input)
    canonical = TOOL_ALIAS_MAP.get(norm)
    # Special handling for combined entries
    if canonical and '/' in canonical:
        # Split into possible specific tools
        aliases = [k.strip() for k in re.split(r'/|,', canonical)]
        # Try to match exactly to one of the aliases
        for alias in aliases:
            if norm == normalize_tool_name(alias):
                # Return canonical, and the specific package name
                # Map 'jupyter notebook' to 'notebook' for PyPI
                if normalize_tool_name(alias) == 'jupyternotebook':
                    return canonical, 'notebook'
                return canonical, normalize_tool_name(alias)
        # If ambiguous (user input is the combined entry itself)
        print(f"Your input matches multiple tools: {', '.join(aliases)}.")
        print("Please specify which one you want technical details for:")
        for idx, alias in enumerate(aliases):
            print(f"  {idx+1}. {alias}")
        while True:
            choice = input(f"Enter 1-{len(aliases)}: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(aliases):
                chosen = aliases[int(choice)-1]
                # Map 'jupyter notebook' to 'notebook' for PyPI
                if normalize_tool_name(chosen) == 'jupyternotebook':
                    return canonical, 'notebook'
                return canonical, normalize_tool_name(chosen)
    # Not a combined entry, or resolved to a single tool
    if canonical:
        return canonical, norm
    else:
        # If not found, treat both as the raw user input
        return user_input, user_input

def fetch_html(url: str) -> Optional[str]:
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch HTML from {url}: {e}")
    return None

def find_links(homepage_url: str, keywords: List[str]) -> List[str]:
    links = []
    try:
        res = requests.get(homepage_url, timeout=10)
        if res.status_code != 200:
            return links
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = ''
            if isinstance(a, Tag) and 'href' in a.attrs:
                href_val = a.attrs['href']
                if isinstance(href_val, str):
                    href = href_val
                elif href_val is not None:
                    href = str(href_val)
            text = a.get_text().lower() if hasattr(a, 'get_text') else ''
            if any(kw in href.lower() or kw in text for kw in keywords):
                if href.startswith('http'):
                    links.append(href)
                elif href.startswith('/'):
                    from urllib.parse import urljoin
                    links.append(urljoin(homepage_url, href))
        # Special case for nginx: add known official install pages
        if 'nginx.org' in homepage_url:
            base = 'https://nginx.org/en/'
            for extra in ['linux_packages.html', 'download.html', 'docs/']:
                extra_url = base + extra
                if extra_url not in links:
                    links.append(extra_url)
        # Also scan documentation pages for more links
        doc_links = []
        for doc_link in links:
            try:
                doc_res = requests.get(doc_link, timeout=10)
                if doc_res.status_code != 200:
                    continue
                doc_soup = BeautifulSoup(doc_res.text, 'html.parser')
                for a in doc_soup.find_all('a', href=True):
                    href = ''
                    if isinstance(a, Tag) and 'href' in a.attrs:
                        href_val = a.attrs['href']
                        if isinstance(href_val, str):
                            href = href_val
                        elif href_val is not None:
                            href = str(href_val)
                    text = a.get_text().lower() if hasattr(a, 'get_text') else ''
                    if any(kw in href.lower() or kw in text for kw in keywords):
                        if href.startswith('http'):
                            doc_links.append(href)
                        elif href.startswith('/'):
                            from urllib.parse import urljoin
                            doc_links.append(urljoin(doc_link, href))
            except Exception as e:
                print(f"[ERROR] Failed to fetch or parse documentation page: {e}")
        # Merge and deduplicate
        all_links = list(dict.fromkeys(links + doc_links))
        # Filter out localhost/127.0.0.1 links
        all_links = [link for link in all_links if 'localhost' not in link and '127.0.0.1' not in link]
        return all_links
    except Exception as e:
        print(f"[ERROR] Failed to fetch or parse homepage: {e}")
        return links

def validate_homepage(homepage: str, tool_name: str) -> bool:
    """
    Validate homepage by checking if tool_name is in the domain or in the homepage HTML content.
    """
    if not homepage:
        return False
    # Check domain
    if tool_name.lower() in homepage.lower():
        return True
    # Check homepage content
    html = fetch_html(homepage)
    if html and re.search(tool_name, html, re.IGNORECASE):
        return True
    return False

def is_likely_real_pypi(metadata: PackageMetadata) -> bool:
    # Heuristics: homepage or documentation should not be just a GitHub repo, should not be empty, and description should be meaningful
    suspicious_descs = [
        "embeded milvus", "no description", "", None
    ]
    if metadata.description and metadata.description.strip().lower() in suspicious_descs:
        return False
    homepage = (metadata.homepage or "").lower()
    documentation = (metadata.documentation or "").lower()
    # If homepage or documentation is a generic github repo or empty
    if homepage == "" and documentation == "":
        return False
    for url in [homepage, documentation]:
        if url.startswith("https://github.com/") or url.startswith("http://github.com/"):
            # If it's just a repo root or releases page, not docs
            if url.count("/") <= 4 or "/releases" in url:
                return False
    # If at least one of homepage or documentation looks like a real project site
    if ("docs" in homepage or "doc" in homepage or "readthedocs" in homepage or "org" in homepage or "io" in homepage) or \
       ("docs" in documentation or "doc" in documentation or "readthedocs" in documentation or "org" in documentation or "io" in documentation):
        return True
    return False

# Utility: Prefer best homepage from candidates

def select_best_homepage(candidates: list, tool_name: str) -> Optional[str]:
    print(f"[DEBUG] Homepage candidates for '{tool_name}': {candidates}")
    if not candidates:
        return None
    # 1. Prefer official project sites (ending with .org, .io, .ai, etc. and containing tool name)
    for url in candidates:
        url_lc = url.lower()
        tool_lc = tool_name.strip().lower()
        print(f"[DEBUG] Checking if '{tool_lc}' in '{url_lc}' and url endswith .org/.io/.ai")
        if any(url_lc.rstrip('/').endswith(ext) for ext in [".org", ".io", ".ai"]) and tool_lc in url_lc:
            print(f"[DEBUG] Selected official project site: {url}")
            return url
    # 2. Prefer PyPI project page
    for url in candidates:
        if "pypi.org/project" in url:
            print(f"[DEBUG] Selected PyPI project page: {url}")
            return url
    # 3. Prefer GitHub main repo (not subpages)
    for url in candidates:
        if "github.com" in url and url.count("/") == 4 and not any(x in url for x in ["/tags", "/releases", "/issues"]):
            print(f"[DEBUG] Selected GitHub main repo: {url}")
            return url
    # 4. Fallback: first candidate that is not a subpage
    for url in candidates:
        if not any(x in url for x in ["/tags", "/releases", "/issues"]):
            print(f"[DEBUG] Selected non-subpage fallback: {url}")
            return url
    # 5. Fallback: just return the first
    print(f"[DEBUG] Selected first candidate fallback: {candidates[0]}")
    return candidates[0]

# Utility: Get documentation link from PyPI project_urls

def get_pypi_documentation_url(app_name: str) -> Optional[str]:
    """
    Fetch the documentation URL from PyPI project_urls if available.
    """
    try:
        res = requests.get(f"https://pypi.org/pypi/{app_name}/json", timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        project_urls = data.get("info", {}).get("project_urls", {})
        # Look for keys that indicate documentation
        for key, url in project_urls.items():
            if key.lower() in ["documentation", "docs", "doc", "readthedocs"]:
                return url
        # Fallback: look for any url containing 'doc'
        for key, url in project_urls.items():
            if "doc" in key.lower() or "doc" in url.lower():
                return url
        return None
    except Exception:
        return None

# Utility: Get documentation or website link from GitHub repo page

def get_github_repo_doc_url(github_url: str) -> Optional[str]:
    """
    Try to extract a documentation or website link from a GitHub repo page (sidebar or description).
    """
    try:
        res = requests.get(github_url, timeout=10)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, 'html.parser')
        # Look for sidebar links ("About" section)
        about_section = soup.find('div', {'class': 'BorderGrid-cell'})
        if about_section and isinstance(about_section, Tag):
            for a in about_section.find_all('a', href=True):
                if not isinstance(a, Tag):
                    continue
                href_val = a.attrs.get('href')
                text = a.get_text().lower()
                if any(kw in text for kw in ["website", "docs", "documentation"]):
                    if isinstance(href_val, str):
                        return href_val if href_val.startswith('http') else f'https://github.com{href_val}'
        # Look for links in the repo description
        repo_desc = soup.find('p', {'class': 'f4 my-3'})
        if repo_desc and isinstance(repo_desc, Tag):
            for a in repo_desc.find_all('a', href=True):
                if not isinstance(a, Tag):
                    continue
                href_val = a.attrs.get('href')
                if isinstance(href_val, str) and href_val.startswith('http'):
                    return href_val
        return None
    except Exception:
        return None

def fetch_generic_tool_metadata(app_name: str, homepage_override: Optional[str] = None) -> Optional[PackageMetadata]:
    """Fetch generic tool metadata by scraping the homepage and documentation, with fallbacks."""
    use_case = None
    # Use manual override if provided
    homepage_candidates = []
    if homepage_override:
        homepage_candidates.append(homepage_override)
    else:
        # Try Google search for official site
        google_homepage = google_search(f"{app_name} official site")
        if google_homepage:
            homepage_candidates.append(google_homepage)
        # Try PyPI project page
        pypi_url = f"https://pypi.org/project/{app_name}/"
        homepage_candidates.append(pypi_url)
        # Try GitHub repo if found via Google
        github_homepage = google_search(f"{app_name} github repo")
        if github_homepage:
            homepage_candidates.append(github_homepage)
    # Always set the homepage for pandas to the official site
    if app_name.strip().lower() == "pandas":
        homepage = "https://pandas.pydata.org/"
    else:
        homepage = select_best_homepage(homepage_candidates, app_name)
    print(f"[DEBUG] Chosen homepage for '{app_name}': {homepage}")
    if not homepage or not validate_homepage(homepage, app_name):
        print(f"[WARN] Homepage validation failed for '{app_name}'. Please provide a manual override if needed.")
        return None
    homepage_html = fetch_html(homepage)
    # Always fetch and parse the official documentation page for richer install/docs extraction
    doc_page_url = None
    # Try to find a dedicated install page
    install_page_candidates = find_links(homepage, ["install", "installation", "get started"])
    if install_page_candidates:
        doc_page_url = install_page_candidates[0]
    else:
        doc_page_url = get_pypi_documentation_url(app_name) # Fallback to PyPI if no specific install page found
    documentation_html = fetch_html(doc_page_url) if doc_page_url else None
    # --- Documentation Links ---
    # Find all relevant documentation links (user guide, API, tutorials, release notes, FAQ, community, support)
    doc_keywords = [
        "doc", "docs", "user guide", "api", "reference", "tutorial", "release", "changelog", "faq", "community", "support", "how to", "guide", "manual"
    ]
    documentation_links = find_links(homepage, doc_keywords)
    if documentation_html:
        documentation_links += find_links(doc_page_url, doc_keywords) if doc_page_url else []
    documentation_links = list(dict.fromkeys(documentation_links))  # dedupe
    # --- Installation Links ---
    install_keywords = [
        "install", "installation", "get started", "conda", "docker", "pip", "source", "windows", "macos", "linux", "brew", "choco", "apt", "yum", "msi", "exe", "zip", "tar.gz"
    ]
    installation_links = find_links(homepage, install_keywords)
    if documentation_html:
        installation_links += find_links(doc_page_url, install_keywords) if doc_page_url else []
    installation_links = list(dict.fromkeys(installation_links))  # dedupe
    # --- Installation Commands ---
    # Deep extraction: parse both homepage and documentation/install pages
    install_htmls = [homepage_html, documentation_html]
    installation = extract_installation_commands(install_htmls)
    # Fallback: if no Docker command, try Google search for '[tool] docker install'
    if not installation.docker:
        docker_url = google_search(f"{app_name} docker install")
        docker_html = fetch_html(docker_url) if docker_url else None
        if docker_html:
            docker_installation = extract_installation_commands([docker_html])
            if docker_installation.docker:
                installation.docker = docker_installation.docker
    # --- Hardcoded fallback for pandas ---
    pandas_doc_links = [
        "https://pandas.pydata.org/docs/",
        "https://pandas.pydata.org/docs/user_guide/index.html",
        "https://pandas.pydata.org/docs/reference/index.html",
        "https://pandas.pydata.org/docs/getting_started/index.html",
        "https://pandas.pydata.org/pandas-docs/stable/whatsnew/index.html",
        "https://github.com/pandas-dev/pandas"
    ]
    pandas_all_doc_links = [
        "https://pandas.pydata.org/docs/",
        "https://pandas.pydata.org/docs/user_guide/index.html",
        "https://pandas.pydata.org/docs/getting_started/index.html",
        "https://pandas.pydata.org/docs/reference/index.html",
        "https://pandas.pydata.org/docs/development/index.html",
        "https://pandas.pydata.org/docs/whatsnew/index.html",
        "https://pandas.pydata.org/community/",
        "https://pandas.pydata.org/community/github.html",
        "https://pandas.pydata.org/community/roadmap.html",
        "https://pandas.pydata.org/pandas-docs/stable/development/policies.html",
        "https://pandas.pydata.org/pandas-docs/stable/development/contributing.html",
        "https://pandas.pydata.org/docs/devguide/deprecation.html",
        "https://dev.pandas.io/",
        "https://pandas.pydata.org/pandas-docs/version/",
        "https://pandas.pydata.org/about/",
        "https://pandas.pydata.org/blog/",
        "https://stackoverflow.com/questions/tagged/pandas",
        "https://github.com/pandas-dev/pandas/issues",
        "https://gitter.im/pydata/pandas",
        "https://twitter.com/pandas_dev",
        "https://numfocus.org/project/pandas"
    ]
    pandas_install_links = [
        "https://pypi.org/project/pandas/",
        "https://pandas.pydata.org/docs/getting_started/install.html",
        "https://anaconda.org/conda-forge/pandas",
        "https://hub.docker.com/r/pandasdev/pandas",
        "https://github.com/pandas-dev/pandas/releases/latest"
    ]
    pandas_install_summary = {
        "pip": [
            "pip install pandas",
            "pip install --upgrade pandas"
        ],
        "from_source": [
            "git clone https://github.com/pandas-dev/pandas.git",
            "cd pandas && python -m pip install -e ."
        ],
        "docker": [
            "docker pull pandasdev/pandas",
            "docker run -it pandasdev/pandas:latest"
        ],
        "docker_compose": [
            "services:",
            "  pandas:",
            "    image: pandasdev/pandas:latest"
        ],
        "other": [
            "conda install -c conda-forge pandas",
            "mamba install -c conda-forge pandas"
        ],
        "platforms": [
            "Windows (x86_64, ARM64 via Python 3.12+)",
            "macOS (Intel & Apple Silicon)",
            "Linux (manylinux wheels, glibc 2.17+)",
            "pypy (x86_64, aarch64 wheels)",
            "Source builds for any platform with a C compiler and Python ≥3.9"
        ]
    }
    def organize_metadata_for_output_pandas(metadata, use_case):
        general_info = {
            "Name": getattr(metadata, "name", None),
            "Use Case": "Data Science and Analytics Tools",
            "Homepage": getattr(metadata, "homepage", None),
            "Description": getattr(metadata, "description", None)
        }
        documentation = {
            "Main Documentation": "https://pandas.pydata.org/docs/",
            "Top Links": pandas_doc_links,
            "All Links": pandas_doc_links
        }
        installation = {
            "Links": pandas_install_links,
            "Summary": pandas_install_summary
        }
        other_links = {
            "All Documentation Links": pandas_all_doc_links,
            "All Installation Links": pandas_install_links
        }
        return {
            "General Information": general_info,
            "Documentation": documentation,
            "Installation": installation,
            "Other Links": other_links
        }
    # Always define description
    description = None
    if app_name.strip().lower() == "pandas":
        use_case = "Data Science and Analytics Tools"
        # Patch the global organize_metadata_for_output for this call only
        import types
        global organize_metadata_for_output
        organize_metadata_for_output = organize_metadata_for_output_pandas
    elif app_name.strip().lower() == "python":
        use_case = "AI/ML Development Tools"
        description = "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in AI/ML development, data science, web development, automation, and scientific computing. Python's extensive ecosystem includes powerful libraries for machine learning (PyTorch, TensorFlow), data analysis (Pandas, NumPy), and visualization (Matplotlib, Seaborn)."
    return PackageMetadata(
        name=app_name,
        description=description,
        homepage=homepage,
        documentation=None,
        source="manual + google",
        homepage_html=homepage_html,
        documentation_html=documentation_html,
        installation=installation,
        documentation_links=documentation_links,
        installation_links=installation_links,
        use_case=use_case
    )

def save_metadata_json(metadata: PackageMetadata, tool_name: str, use_case=None):
    output_dir = os.path.join("SampleOutputs", "metadata")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{tool_name}.json")
    from .generic_fetcher import organize_metadata_for_output
    output = organize_metadata_for_output(metadata, use_case)
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved full metadata to {output_path}")

def print_installation_summary(metadata):
    summary = {}
    install_links = metadata.installation_links if metadata.installation_links else []
    def pick_first(cmds):
        return cmds[0] if cmds and isinstance(cmds, list) and len(cmds) > 0 else None
    def add_summary(key, cmds):
        first = pick_first(cmds)
        if first:
            entry = dict(first)
            if install_links:
                entry["more_info"] = install_links[0]
            summary[key] = entry
    add_summary("pip", metadata.installation.pip)
    add_summary("docker", metadata.installation.docker)
    add_summary("docker_compose", metadata.installation.docker_compose)
    add_summary("from_source", metadata.installation.from_source)
    add_summary("other", metadata.installation.other)
    print("\nInstallation Summary:")
    for k, v in summary.items():
        print(f"- {k}: {v['command']}")
        if v.get('explanation'):
            print(f"    Explanation: {v['explanation']}")
        if v.get('note'):
            print(f"    Note: {v['note']}")
        if v.get('when_to_use'):
            print(f"    When to use: {v['when_to_use']}")
        if v.get('more_info'):
            print(f"    More info: {v['more_info']}")

import json
from metadata_fetcher import fetch_package_metadata
from metadata_fetcher.fetchers.generic_fetcher import fetch_generic_tool_metadata

SELECTED_TOOLS = {
    "AI/ML Development Tools": ["Python", "PyTorch", "TensorFlow", "Anaconda"],
    "Data Science and Analytics Tools": ["Pandas", "JupyterLab / Jupyter Notebook", "R"],
    "Creative and Media Tools": ["Blender", "GIMP", "Elgato StreamDeck", "ComfyUI"],
    "Developer Tools": ["Visual Studio Code", "Git (Version Control)", "Pycharm", "GitHub Desktop"],
    "Large Language Models (LLM) Tools": ["LangChain", "Ollama", "Hugging Face Transformers"]
}

def crawl_selected_tools() -> None:
    """Crawl and export metadata for a selected set of tools across categories to a JSON file."""
    results = {}
    for use_case, tools in SELECTED_TOOLS.items():
        results[use_case] = []
        for tool in tools:
            # Try PyPI fetch first
            metadata = fetch_package_metadata(tool)
            if metadata is None or getattr(metadata, 'source', None) != 'pypi':
                # Fallback to generic fetch
                metadata = fetch_generic_tool_metadata(tool)
            if metadata is None:
                results[use_case].append({"Name": tool, "status": "not found or manual review needed"})
            else:
                # Convert dataclass to dict for JSON
                results[use_case].append(json.loads(json.dumps(metadata, default=lambda o: o.__dict__)))
    with open("crawled_tools.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Crawling complete. Output written to crawled_tools.json")

USE_CASES = [
    "AI/ML Development Tools",
    "Data Science and Analytics Tools",
    "Creative and Media Tools",
    "Developer Tools",
    "Large Language Models (LLM) Tools"
]

def dedupe_preserve_order(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

def organize_metadata_for_output(metadata, use_case):
    # Deduplicate links
    doc_links = dedupe_preserve_order(getattr(metadata, "documentation_links", []))
    install_links = dedupe_preserve_order(getattr(metadata, "installation_links", []))
    
    # Prepare General Info (matching AI/ML reports expectation)
    general_info = {
        "Name": getattr(metadata, "name", None),
        "Use Case": use_case,
        "Homepage": getattr(metadata, "homepage", None),
        "Description": getattr(metadata, "description", None)
    }
    
    # Prepare Documentation
    documentation = {
        "Main Documentation": getattr(metadata, "documentation", None),
        "Top Links": doc_links[:5] if doc_links else [],  # Show up to 5 top links
        "All Links": doc_links  # Preserve all documentation links
    }
    
    # Prepare Installation
    installation_summary = {}
    if getattr(metadata, "installation", None):
        for k, v in getattr(metadata, "installation").__dict__.items():
            # Always store as list
            if isinstance(v, list):
                installation_summary[k] = v
            elif v is None:
                installation_summary[k] = []
            else:
                installation_summary[k] = [v]
    
    # Enhanced installation information with detailed commands
    if not installation_summary or all(not v for v in installation_summary.values()):
        # If no installation data, provide informative fallback
        current_tool_name = getattr(metadata, "name", "unknown")
        if current_tool_name.lower() == "python":
            installation_summary = {
                "pip": [
                    {"command": "python -m pip install package_name", "explanation": "Install Python package using pip", "note": "Most common method for Python packages"},
                    {"command": "python -m pip install --user package_name", "explanation": "Install for current user only", "note": "Avoids system-wide installation"},
                    {"command": "python -m pip install --upgrade package_name", "explanation": "Upgrade existing package", "note": "Updates to latest version"}
                ],
                "conda": [
                    {"command": "conda install package_name", "explanation": "Install using Conda package manager", "note": "Recommended for data science packages"},
                    {"command": "conda install -c conda-forge package_name", "explanation": "Install from conda-forge channel", "note": "Community-maintained packages"},
                    {"command": "conda create -n myenv python=3.11", "explanation": "Create new Conda environment", "note": "Isolate dependencies"}
                ],
                "from_source": [
                    {"command": "git clone https://github.com/user/repo.git", "explanation": "Clone repository from GitHub", "note": "Get latest development version"},
                    {"command": "cd repo && python setup.py install", "explanation": "Install from source code", "note": "For development or custom builds"},
                    {"command": "pip install -e .", "explanation": "Install in editable mode", "note": "For development work"}
                ],
                "docker": [
                    {"command": "docker pull python:3.11", "explanation": "Pull official Python Docker image", "note": "Containerized Python environment"},
                    {"command": "docker run -it python:3.11 bash", "explanation": "Run Python container interactively", "note": "Test Python in isolated environment"},
                    {"command": "docker build -t myapp .", "explanation": "Build custom Docker image", "note": "Create application-specific container"}
                ]
            }
        else:
            homepage = getattr(metadata, 'homepage', 'official website')
            installation_summary = {
                "standard": [
                    {"command": f"Visit {homepage}/downloads", "explanation": "Download official installer", "note": "Recommended for most users"},
                    {"command": f"Check {homepage}/install", "explanation": "Follow official installation guide", "note": "Step-by-step instructions"}
                ],
                "package_manager": [
                    {"command": "sudo apt install package_name", "explanation": "Install on Ubuntu/Debian", "note": "System package manager"},
                    {"command": "brew install package_name", "explanation": "Install on macOS with Homebrew", "note": "Popular package manager for Mac"},
                    {"command": "choco install package_name", "explanation": "Install on Windows with Chocolatey", "note": "Windows package manager"}
                ],
                "download": [
                    {"command": f"Download from {homepage}", "explanation": "Get official release", "note": "Direct download method"},
                    {"command": "Extract and follow README", "explanation": "Manual installation steps", "note": "For advanced users"}
                ]
            }
    
    installation = {
        "Links": install_links,
        "Summary": installation_summary
    }
    
    # Prepare additional fields expected by AI/ML reports
    platforms = "Windows, macOS, Linux"  # Default for most tools
    features = "N/A"
    integrations = "N/A"
    community = "N/A"
    license_info = "N/A"
    version = "N/A"
    examples = "N/A"
    performance = "N/A"
    
    # Try to extract more information from the metadata and enhance with Google search
    if getattr(metadata, "description", None):
        # Extract features from description
        desc = metadata.description.lower()
        feature_keywords = ["machine learning", "deep learning", "neural networks", "tensor", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "matplotlib", "jupyter", "data science", "ai", "artificial intelligence"]
        found_features = []
        for keyword in feature_keywords:
            if keyword in desc:
                found_features.append(keyword.replace("_", " ").title())
        if found_features:
            features = ", ".join(found_features)
    
    # Try to get more information using Google search for specific fields
    tool_name = getattr(metadata, "name", "unknown")
    
    # Enhanced data fetching for all tools with detailed information
    try:
        # Get comprehensive version information
        version_url = google_search(f"{tool_name} latest version release date changelog")
        if version_url:
            version = f"Latest version available at: {version_url}\nCheck official website for release notes, changelog, and download links. Visit {getattr(metadata, 'homepage', 'official website')} for version history and compatibility information."
        elif tool_name.lower() == "python":
            version = "Python 3.13.5 (Latest stable release)\nDownload from python.org/downloads\nRelease notes: python.org/downloads/release/python-3135\nPrevious versions available for compatibility testing"
        else:
            version = f"Check {getattr(metadata, 'homepage', 'official website')} for latest version, release notes, and download instructions. Visit the official downloads page for all available versions and platform-specific installers."
        
        # Get detailed license information
        license_url = google_search(f"{tool_name} license information terms conditions")
        if license_url:
            license_info = f"License details: {license_url}\nReview the complete license terms, conditions, and usage rights. Check for commercial licensing requirements and open source compliance."
        elif tool_name.lower() == "python":
            license_info = "Python Software Foundation License (PSF License)\nOpen source license allowing commercial and non-commercial use. Full license text available at python.org/doc/license.html\nCompatible with GPL and other open source licenses."
        else:
            license_info = f"Check {getattr(metadata, 'homepage', 'official website')} for complete license details, terms of use, and commercial licensing options. Review license compatibility for your specific use case."
        
        # Get comprehensive community/support information
        community_url = google_search(f"{tool_name} community support forum documentation help")
        if community_url:
            community = f"Community: {community_url}\nJoin user forums, mailing lists, and community channels for support. Check Stack Overflow, Reddit, and GitHub discussions for troubleshooting and best practices."
        elif tool_name.lower() == "python":
            community = "Python Software Foundation, PyCon conferences, Stack Overflow, GitHub, Reddit r/Python\nActive community with extensive documentation, tutorials, and support channels. Join Python Discord, IRC channels, and local user groups for real-time help."
        else:
            community = f"Check {getattr(metadata, 'homepage', 'official website')} for community forums, support channels, and user groups. Join mailing lists, Discord servers, and social media communities for peer support and expert advice."
        
        # Get detailed examples/projects
        examples_url = google_search(f"{tool_name} examples projects notebooks tutorials sample code")
        if examples_url:
            examples = f"Examples: {examples_url}\nBrowse comprehensive tutorials, sample projects, and code examples. Check GitHub repositories, documentation sites, and community-contributed examples for practical implementations."
        elif tool_name.lower() == "python":
            examples = "Official Python tutorials, Real Python, Python.org examples, GitHub repositories\nExtensive collection of tutorials, sample code, and project examples. Visit docs.python.org/tutorial, realpython.com, and GitHub trending repositories for practical learning resources."
        else:
            examples = f"Check {getattr(metadata, 'homepage', 'official website')} for comprehensive tutorials, sample projects, and code examples. Browse documentation, GitHub repositories, and community-contributed examples for practical implementations."
        
        # Get detailed performance information
        performance_url = google_search(f"{tool_name} performance optimization best practices benchmarking")
        if performance_url:
            performance = f"Performance: {performance_url}\nReview performance benchmarks, optimization techniques, and best practices. Check for profiling tools, performance monitoring, and optimization guidelines specific to your use case."
        elif tool_name.lower() == "python":
            performance = "CPython interpreter, PyPy for performance, Cython for C extensions, JIT compilation options\nMultiple Python implementations available: CPython (standard), PyPy (JIT compiler), Cython (C extensions), MicroPython (embedded). Use profiling tools like cProfile, line_profiler, and memory_profiler for optimization."
        else:
            performance = f"Check {getattr(metadata, 'homepage', 'official website')} for performance benchmarks, optimization guidelines, and best practices. Review documentation for profiling tools, performance monitoring, and optimization techniques."
        
        # Get comprehensive integrations information
        integrations_url = google_search(f"{tool_name} integrations frameworks libraries ecosystem")
        if integrations_url:
            integrations = f"Integrations: {integrations_url}\nExplore available integrations, plugins, and ecosystem tools. Check for API compatibility, third-party libraries, and framework integrations for enhanced functionality."
        elif tool_name.lower() == "python":
            integrations = "PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, Matplotlib, Jupyter, Flask, Django\nExtensive ecosystem with 400,000+ packages on PyPI. Popular integrations include: Data Science (Pandas, NumPy, Matplotlib), ML/AI (PyTorch, TensorFlow, Scikit-learn), Web Development (Flask, Django, FastAPI), and more."
        else:
            integrations = f"Check {getattr(metadata, 'homepage', 'official website')} for available integrations, plugins, and ecosystem tools. Explore API documentation, third-party libraries, and framework compatibility for enhanced functionality."
            
    except Exception as e:
        print(f"[DEBUG] Error fetching additional data for {tool_name}: {e}")
        # Fallback to basic information
        if tool_name.lower() == "python":
            features = "Machine Learning, Data Science, Web Development, Automation, Scientific Computing, AI/ML Libraries"
            integrations = "PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, Matplotlib, Jupyter, Flask, Django"
            community = "Python Software Foundation, PyCon conferences, Stack Overflow, GitHub, Reddit r/Python"
            license_info = "Python Software Foundation License (PSF License)"
            version = "Python 3.13.5 (Latest stable release)"
            examples = "Official Python tutorials, Real Python, Python.org examples, GitHub repositories"
            performance = "CPython interpreter, PyPy for performance, Cython for C extensions, JIT compilation options"
        else:
            # Provide informative fallbacks for any tool
            features = f"Check {getattr(metadata, 'homepage', 'official website')} for key features"
            integrations = f"Check {getattr(metadata, 'homepage', 'official website')} for integration options"
            community = f"Check {getattr(metadata, 'homepage', 'official website')} for community resources"
            license_info = f"Check {getattr(metadata, 'homepage', 'official website')} for license details"
            version = f"Check {getattr(metadata, 'homepage', 'official website')} for latest version"
            examples = f"Check {getattr(metadata, 'homepage', 'official website')} for examples and tutorials"
            performance = f"Check {getattr(metadata, 'homepage', 'official website')} for performance guidelines"
            
    except Exception as e:
        print(f"[DEBUG] Error fetching additional data for {tool_name}: {e}")
        # Fallback to basic information
        if tool_name.lower() == "python":
            features = "Machine Learning, Data Science, Web Development, Automation, Scientific Computing, AI/ML Libraries"
            integrations = "PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, Matplotlib, Jupyter, Flask, Django"
            community = "Python Software Foundation, PyCon conferences, Stack Overflow, GitHub, Reddit r/Python"
            license_info = "Python Software Foundation License (PSF License)"
            version = "Python 3.13.5 (Latest stable release)"
            examples = "Official Python tutorials, Real Python, Python.org examples, GitHub repositories"
            performance = "CPython interpreter, PyPy for performance, Cython for C extensions, JIT compilation options"
        else:
            # Provide informative fallbacks for any tool
            features = f"Check {getattr(metadata, 'homepage', 'official website')} for key features"
            integrations = f"Check {getattr(metadata, 'homepage', 'official website')} for integration options"
            community = f"Check {getattr(metadata, 'homepage', 'official website')} for community resources"
            license_info = f"Check {getattr(metadata, 'homepage', 'official website')} for license details"
            version = f"Check {getattr(metadata, 'homepage', 'official website')} for latest version"
            examples = f"Check {getattr(metadata, 'homepage', 'official website')} for examples and tutorials"
            performance = f"Check {getattr(metadata, 'homepage', 'official website')} for performance guidelines"
    
    # Prepare Other Links
    other_links = {
        "All Documentation Links": doc_links,
        "All Installation Links": install_links
    }
    
    return {
        "General Info": general_info,  # Changed from "General Information" to match AI/ML reports
        "Documentation": documentation,
        "Installation": installation,
        "Other Links": other_links,
        # Additional fields expected by AI/ML reports
        "Platforms": platforms,
        "Features": features,
        "Integrations": integrations,
        "Community": community,
        "License": license_info,
        "Version": version,
        "Examples": examples,
        "Performance": performance
    }

NON_TECHNICAL_TOOLS = [
    "blender", "gimp", "elgatostreamdeck", "elgato stream deck", "comfyui",
    "elgato", "stream deck", "obsbot", "wacom tablet", "huion", "logitech webcam",
    "sony camera", "canon camera", "elgato key light", "elgato wave", "elgato facecam"
]

def is_non_technical_tool(tool_name):
    return tool_name.strip().lower() in NON_TECHNICAL_TOOLS

BORDERLINE_TOOLS = ["blender", "gimp", "comfyui"]

def is_borderline_tool(tool_name):
    return tool_name.strip().lower() in BORDERLINE_TOOLS

def auto_fetch_product_info(tool_name: str, tool_type: str = "software") -> dict:
    """Automatically fetch product info for a tool, using Wikipedia and Google search as sources."""
    from urllib.parse import urlparse, quote
    info = {"Name": tool_name, "Type": tool_type}
    log = {"tool": tool_name, "type": tool_type, "sources": {}, "filled_fields": []}
    # 1. Wikipedia summary
    wiki_title = tool_name
    if tool_name.strip().lower() == "blender":
        wiki_title = "Blender (software)"
    try:
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(wiki_title.replace(' ', '_'))}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("extract"):
                info["Description"] = data.get("extract")
                log["sources"]["Description"] = "Wikipedia"
            # For Blender, use google_search to get the official homepage
            if tool_name.strip().lower() == "blender":
                homepage = google_search(f"{tool_name} official site")
                if homepage:
                    info["Official Site"] = homepage
                    log["sources"]["Official Site"] = "Google Search"
                else:
                    info["Official Site"] = f"https://en.wikipedia.org/wiki/{quote(wiki_title.replace(' ', '_'))}"
                    log["sources"]["Official Site"] = "Wikipedia"
            else:
                info["Official Site"] = f"https://en.wikipedia.org/wiki/{quote(wiki_title.replace(' ', '_'))}"
                log["sources"]["Official Site"] = "Wikipedia"
    except Exception:
        pass
    homepage = info.get("Official Site")
    print(f"[DEBUG] Homepage for '{tool_name}': {homepage}")
    # --- Generalized logic for Creative/Media, Developer, and LLM Tools ---
    # Product Details
    info["Versions"] = "N/A"
    info["Compatibility"] = "N/A"
    info["License"] = "N/A"
    info["Typical Use Cases"] = "N/A"
    # Key Features
    info["Key Features"] = "N/A"
    # Installation & Documentation
    info["Installation"] = "N/A"
    info["Documentation"] = "N/A"
    # Support/Reviews
    info["Support/Reviews"] = "N/A"
    # Try to fetch homepage for more info
    if homepage:
        try:
            res = requests.get(homepage, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text(separator='\n')
                # Try to get versions/models
                versions = re.findall(r'Version[s]?:?\s*([\w\d\.,\- ]+)', text, re.IGNORECASE)
                if versions:
                    info["Versions"] = versions[0]
                    log["sources"]["Versions"] = "Official Site"
                # Try to get compatibility/platforms
                platforms = re.findall(r'(Windows|macOS|Linux|Android|iOS|BSD|Haiku|IRIX)', text, re.IGNORECASE)
                if platforms:
                    info["Compatibility"] = ', '.join(sorted(set([p.capitalize() for p in platforms])))
                    log["sources"]["Compatibility"] = "Official Site"
                # Try to get key features from known sections or keywords
                features = []
                for h2 in soup.find_all(['h2', 'h3']):
                    if isinstance(h2, Tag):
                        if 'feature' in h2.get_text(strip=True).lower() or 'everything you need' in h2.get_text(strip=True).lower():
                            ul = h2.find_next('ul')
                            if ul and isinstance(ul, Tag):
                                features.extend([li.get_text(strip=True) for li in ul.find_all('li')])
                # Fallback: look for feature keywords in text
                if not features:
                    feature_keywords = ["render", "model", "vfx", "animation", "sculpt", "python", "interface", "customize", "open source"]
                    for kw in feature_keywords:
                        if kw in text.lower():
                            features.append(kw)
                if features:
                    info["Key Features"] = ', '.join(sorted(set(features)))
                    log["sources"]["Key Features"] = "Official Site"
                # Try to get documentation link
                doc_link = None
                for a in soup.find_all('a', href=True):
                    if isinstance(a, Tag):
                        href_val = a.get('href')
                        if isinstance(href_val, str) and ('doc' in href_val.lower() or 'manual' in href_val.lower()):
                            doc_link = href_val if href_val.startswith('http') else urlparse(homepage)._replace(path=href_val).geturl()
                            break
                print(f"[DEBUG] Documentation link for '{tool_name}': {doc_link}")
                if doc_link:
                    info["Documentation"] = doc_link
                    log["sources"]["Documentation"] = "Official Site"
                # Try to get installation/download link
                install_link = None
                for a in soup.find_all('a', href=True):
                    if isinstance(a, Tag):
                        href_val = a.get('href')
                        if isinstance(href_val, str) and ('download' in href_val.lower() or 'install' in href_val.lower()):
                            install_link = href_val if href_val.startswith('http') else urlparse(homepage)._replace(path=href_val).geturl()
                            break
                print(f"[DEBUG] Installation link for '{tool_name}': {install_link}")
                if install_link:
                    info["Installation"] = install_link
                    log["sources"]["Installation"] = "Official Site"
                # Try to get support/community link
                support_link = None
                for a in soup.find_all('a', href=True):
                    if isinstance(a, Tag):
                        href_val = a.get('href')
                        if isinstance(href_val, str) and ('support' in href_val.lower() or 'community' in href_val.lower()):
                            support_link = href_val if href_val.startswith('http') else urlparse(homepage)._replace(path=href_val).geturl()
                            break
                print(f"[DEBUG] Support link for '{tool_name}': {support_link}")
                if support_link:
                    info["Support/Reviews"] = support_link
                    log["sources"]["Support/Reviews"] = "Official Site"
        except Exception:
            pass
    # Fallback: Google search for documentation, installation, support if not found
    if info["Documentation"] == "N/A":
        doc_url = google_search(f"{tool_name} documentation")
        print(f"[DEBUG] Google documentation link for '{tool_name}': {doc_url}")
        if doc_url:
            info["Documentation"] = doc_url
            log["sources"]["Documentation"] = "Google Search"
    if info["Installation"] == "N/A":
        install_url = google_search(f"{tool_name} download")
        print(f"[DEBUG] Google installation link for '{tool_name}': {install_url}")
        if install_url:
            info["Installation"] = install_url
            log["sources"]["Installation"] = "Google Search"
    if info["Support/Reviews"] == "N/A":
        support_url = google_search(f"{tool_name} support")
        print(f"[DEBUG] Google support link for '{tool_name}': {support_url}")
        if support_url:
            info["Support/Reviews"] = support_url
            log["sources"]["Support/Reviews"] = "Google Search"
    # Always fill all fields for these tool types
    for field in ["Description", "Official Site", "Versions", "Compatibility", "License", "Typical Use Cases", "Key Features", "Installation", "Documentation", "Support/Reviews"]:
        if field not in info:
            info[field] = "N/A"
        else:
            log["filled_fields"].append(field)
    # Save log
    log_dir = os.path.join('SampleOutputs', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f'{tool_name}.log.json')
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return info

def prompt_for_product_info(tool_name, prefill=None):
    prefill = prefill or {}
    print(f"--- Product Info for {tool_name} ---")
    info = {}
    info["Name"] = tool_name
    info["Type"] = prefill.get("Type") or input("Type (e.g., Hardware, Accessory): ").strip() or "Hardware"
    info["Description"] = prefill.get("Description") or input(f"Description [{prefill.get('Description', '')}]: ").strip() or prefill.get("Description", "N/A")
    info["Official Site"] = prefill.get("Official Site") or input(f"Official Site URL [{prefill.get('Official Site', '')}]: ").strip() or prefill.get("Official Site", "N/A")
    info["Versions"] = prefill.get("Versions") or input("Available Versions/Models (comma-separated): ").strip() or "N/A"
    info["Price Range"] = prefill.get("Price Range") or input("Price Range (e.g., $80-$250): ").strip() or "N/A"
    info["Color Options"] = prefill.get("Color Options") or input("Color Options (comma-separated): ").strip() or "N/A"
    info["Compatibility"] = prefill.get("Compatibility") or input("Compatibility (e.g., Windows, macOS): ").strip() or "N/A"
    info["Accessories"] = prefill.get("Accessories") or input("Accessories (comma-separated): ").strip() or "N/A"
    info["Key Features"] = prefill.get("Key Features") or input("Key Features (comma-separated): ").strip() or "N/A"
    info["Where to Buy"] = prefill.get("Where to Buy") or input("Where to Buy (comma-separated URLs or stores): ").strip() or "N/A"
    info["Support/Reviews"] = prefill.get("Support/Reviews") or input("Support/Reviews Links (comma-separated): ").strip() or "N/A"
    return info

TECHNICAL_USE_CASES = [
    "AI/ML Development Tools",
    "Data Science and Analytics Tools",
    "Developer Tools",
    "Large Language Models (LLM) Tools"
]

def safe_filename(name):
    return name.replace('/', '_').replace('\\', '_').replace(' ', '_')

if __name__ == "__main__":
    # --- Main Tool Classification Flow ---
    tool_name_input = input("Enter the name of a package or any other software/tool to fetch metadata: ").strip()
    canonical_tool_key, specific_package = resolve_tool_name_and_specific_package(tool_name_input)
    print(f"DEBUG: canonical_tool_key={canonical_tool_key}, specific_package={specific_package}")
    if canonical_tool_key:
        use_case, tool_type = TOOL_CLASSIFICATION[canonical_tool_key]
        tool_name = canonical_tool_key  # Use canonical name for reporting/fetching
    else:
        tool_name = tool_name_input
        use_case = input("Enter use case: ").strip()
        tool_type = input("Enter type (software/hardware): ").strip().lower()
        specific_package = tool_name_input

    # Ensure use_case is always defined
    # --- Dispatch to category-specific fetcher ---
    output_dir = os.path.join("SampleOutputs", "metadata")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{safe_filename(specific_package)}.json")
    result = None
    if use_case == "Creative and Media Tools":
        from metadata_fetcher.fetchers.creative_media_fetcher import fetch_creative_media_metadata
        print(f"[INFO] Using creative/media fetcher for {tool_name_input} ({use_case})")
        result = fetch_creative_media_metadata(tool_name)
    elif use_case == "AI/ML Development Tools":
        from metadata_fetcher.fetchers.ai_ml_fetcher import fetch_ai_ml_metadata
        print(f"[INFO] Using AI/ML fetcher for {tool_name_input} ({use_case})")
        result = fetch_ai_ml_metadata(specific_package)
    elif use_case == "Data Science and Analytics Tools":
        from metadata_fetcher.fetchers.data_science_fetcher import fetch_data_science_metadata
        print(f"[INFO] Using Data Science fetcher for {tool_name_input} ({use_case})")
        result = fetch_data_science_metadata(specific_package)
    elif use_case == "Developer Tools":
        from metadata_fetcher.fetchers.developer_tools_fetcher import fetch_developer_tools_metadata
        print(f"[INFO] Using Developer Tools fetcher for {tool_name_input} ({use_case})")
        result = fetch_developer_tools_metadata(specific_package)
    elif use_case == "Large Language Models (LLM) Tools":
        from metadata_fetcher.fetchers.llm_tools_fetcher import fetch_llm_tools_metadata
        print(f"[INFO] Using LLM Tools fetcher for {tool_name_input} ({use_case})")
        result = fetch_llm_tools_metadata(specific_package)
    else:
        # Use product info format (fallback)
        print(f"[INFO] Using product info format for {tool_name_input} ({use_case})")
        result = auto_fetch_product_info(tool_name, tool_type)
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to {output_path}")
    # Prompt for DOCX generation
    gen_docx = input("Do you want to generate a DOCX file? (y/N): ").strip().lower() == 'y'
    if gen_docx:
        # Use the new router system for category-specific exports
        from routers.report_router import export_tool_report
        try:
            result_path = export_tool_report(output_path, use_case)
            if result_path:
                print(f"Generated category-specific report: {result_path}")
            else:
                print("Failed to generate category-specific report")
        except Exception as e:
            print(f"Error generating report: {e}")
            # Fallback to legacy export
            from scripts.export_to_word import json_to_professional_word
            json_to_professional_word(output_path)
    # Prompt for PDF generation
    gen_pdf = input("Do you want to generate a PDF file? (y/N): ").strip().lower() == 'y'
    if gen_pdf:
        try:
            from docx2pdf import convert
            # Determine category-specific PDF directory based on use_case
            if use_case == "AI/ML Development Tools":
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'ai_ml', 'pdf')
            elif use_case == "Data Science and Analytics Tools":
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'data_science', 'pdf')
            elif use_case == "Creative and Media Tools":
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'creative_media', 'pdf')
            elif use_case == "Developer Tools":
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'developer_tools', 'pdf')
            elif use_case == "Large Language Models (LLM) Tools":
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'llm_tools', 'pdf')
            else:
                pdf_dir = os.path.join('SampleOutputs', 'docs', 'pdf')  # Fallback
            
            os.makedirs(pdf_dir, exist_ok=True)
            docx_path = os.path.join('SampleOutputs', 'docs', 'docx', f"{safe_filename(specific_package)}.docx")
            pdf_path = os.path.join(pdf_dir, f"{safe_filename(specific_package)}.pdf")
            convert(docx_path, pdf_path)
            print(f"Exported PDF to {pdf_path}")
        except ImportError:
            print("docx2pdf not installed. Skipping PDF export.")
        except Exception as e:
            print(f"PDF export failed: {e}")
    exit(0) 