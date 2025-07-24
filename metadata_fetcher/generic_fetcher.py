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
from export_to_word import export_product_docx, json_to_professional_word

DOC_KEYWORDS = ["docs", "documentation", "install", "setup", "getting-started", "guide"]
INSTALL_KEYWORDS = ["install", "setup", "getting-started", "quickstart", "start"]

def load_tool_classification():
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
    homepage = select_best_homepage(homepage_candidates, app_name)
    print(f"[DEBUG] Chosen homepage for '{app_name}': {homepage}")
    if not homepage or not validate_homepage(homepage, app_name):
        print(f"[WARN] Homepage validation failed for '{app_name}'. Please provide a manual override if needed.")
        return None
    homepage_html = fetch_html(homepage)
    # Try PyPI for documentation link first
    documentation = get_pypi_documentation_url(app_name)
    documentation_links = []
    if documentation:
        print(f"[DEBUG] PyPI documentation link for '{app_name}': {documentation}")
        documentation_links.append(documentation)
    else:
        # If homepage is a GitHub repo, try to get docs/website link from repo page
        if "github.com" in homepage:
            github_doc = get_github_repo_doc_url(homepage)
            print(f"[DEBUG] GitHub repo doc/website link for '{app_name}': {github_doc}")
            if github_doc:
                documentation = github_doc
                documentation_links.append(github_doc)
        # Fallback: Google search for '[tool name] documentation' if still not found
        if not documentation_links:
            google_doc = google_search(f"{app_name} documentation")
            print(f"[DEBUG] Google documentation link for '{app_name}': {google_doc}")
            if google_doc and (
                (app_name.lower() in google_doc.lower() and any(google_doc.endswith(ext) for ext in [".org", ".io", ".ai"]))
                or "readthedocs" in google_doc
            ):
                documentation = google_doc
                documentation_links.append(google_doc)
        # Fallback: scrape homepage for doc links
        if not documentation_links:
            documentation_links = find_links(homepage, DOC_KEYWORDS)
            print(f"[DEBUG] Scraped documentation links for '{app_name}': {documentation_links}")
            documentation = documentation_links[0] if documentation_links else None
    installation_links = find_links(homepage, INSTALL_KEYWORDS)
    documentation_html = fetch_html(documentation) if documentation else None
    # --- Description Extraction ---
    description = None
    # 1. Try Wikipedia summary
    try:
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{app_name.replace(' ', '_')}")
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract")
            if extract and "may refer to:" not in extract:
                description = extract
    except Exception:
        pass
    # 2. Try meta description from homepage HTML
    if not description and homepage_html:
        try:
            soup = BeautifulSoup(homepage_html, 'html.parser')
            desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if desc_tag and isinstance(desc_tag, Tag) and desc_tag.has_attr('content'):
                description = desc_tag['content']
        except Exception:
            pass
    # 3. Try first non-empty <p> from homepage
    if not description and homepage_html:
        try:
            soup = BeautifulSoup(homepage_html, 'html.parser')
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    description = text
                    break
        except Exception:
            pass
    # Fallback
    if not description or not isinstance(description, str):
        description = None
    # Fetch all installation HTMLs (not just first 3)
    install_htmls = [fetch_html(link) for link in installation_links if link]
    # Use new extraction logic (list of HTMLs)
    installation = extract_installation_commands(install_htmls)
    # Fallback: if no Docker command, try Google search for '[tool] docker install'
    if not installation.docker:
        docker_url = google_search(f"{app_name} docker install")
        docker_html = fetch_html(docker_url) if docker_url else None
        if docker_html:
            docker_installation = extract_installation_commands([docker_html])
            if docker_installation.docker:
                installation.docker = docker_installation.docker
    if not (installation.pip or installation.docker or installation.from_source or installation.other):
        # Fallback: try documentation and homepage HTMLs
        installation = extract_installation_commands([documentation_html, homepage_html])
    return PackageMetadata(
        name=app_name,
        description=description,
        homepage=homepage,
        documentation=documentation,
        source="manual + google",
        homepage_html=homepage_html,
        documentation_html=documentation_html,
        installation=installation,
        documentation_links=documentation_links,
        installation_links=installation_links
    )

def save_metadata_json(metadata: PackageMetadata, tool_name: str):
    # Determine subfolder based on source
    if metadata.source == "pypi":
        subfolder = os.path.join("SampleOutputs", "metadata", "PyPI")
    else:
        subfolder = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
    os.makedirs(subfolder, exist_ok=True)
    output_path = os.path.join(subfolder, f"{tool_name}.json")
    # Only keep summary and relevant links
    summary = {
        "Name": metadata.name,
        "Homepage": metadata.homepage,
        "Documentation": metadata.documentation,
        "Source": metadata.source,
        "Documentation Links": metadata.documentation_links[:5] + (["..."] if len(metadata.documentation_links) > 5 else []),
    }
    # Add Installation Summary
    def pick_first(cmds):
        return cmds[0] if cmds and isinstance(cmds, list) and len(cmds) > 0 else None
    def pick_relevant_link(install_type):
        links = metadata.installation_links if metadata.installation_links else []
        for link in links:
            if install_type in link:
                return link
        return links[0] if links else None
    def add_summary(key, cmds):
        first = pick_first(cmds)
        if first:
            entry = dict(first)
            link = pick_relevant_link(key)
            if link:
                entry["more_info"] = link
            # If 'commands' exists, keep as is; if only 'command', keep as is
            if 'commands' in entry:
                entry['commands'] = entry['commands']  # already a list
                entry.pop('command', None)  # remove single command if present
            return entry
        return None
    installation_summary = {}
    for key, cmds in [
        ("pip", metadata.installation.pip),
        ("docker", metadata.installation.docker),
        ("docker_compose", metadata.installation.docker_compose),
        ("from_source", metadata.installation.from_source),
        ("other", metadata.installation.other)
    ]:
        entry = add_summary(key, cmds)
        if entry:
            installation_summary[key] = entry
    summary["Installation Summary"] = installation_summary
    if not installation_summary:
        summary["note"] = "No installation commands found. Please refer to the documentation links."
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved summary metadata to {output_path}")

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
from metadata_fetcher.generic_fetcher import fetch_generic_tool_metadata

SELECTED_TOOLS = {
    "AI/ML Development Tools": ["Python", "PyTorch", "TensorFlow", "Anaconda"],
    "Data Science and Analytics Tools": ["Pandas", "JupyterLab / Jupyter Notebook", "R"],
    "Creative and Media Tools": ["Blender", "GIMP", "Elgato StreamDeck", "ComfyUI"],
    "Developer Tools": ["Visual Studio Code", "Git (Version Control)", "Pycharm", "GitHub Desktop"],
    "Large Language Models (LLM) Tools": ["LangChain", "Ollama", "Hugging Face Transformers"]
}

def crawl_selected_tools():
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
    # Prepare General Info
    general_info = {
        "Name": getattr(metadata, "name", None),
        "Use Case": use_case,
        "Homepage": getattr(metadata, "homepage", None),
        "Description": getattr(metadata, "description", None)
    }
    # Prepare Documentation
    documentation = {
        "Main Documentation": getattr(metadata, "documentation", None),
        "Top Links": doc_links[:3] if doc_links else []
    }
    # Prepare Installation
    installation = {
        "Links": install_links,
        "Summary": getattr(metadata, "installation", None).__dict__ if getattr(metadata, "installation", None) else {}
    }
    # Prepare Other Links
    other_links = {
        "All Documentation Links": doc_links,
        "All Installation Links": install_links
    }
    return {
        "General Info": general_info,
        "Documentation": documentation,
        "Installation": installation,
        "Other Links": other_links
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

def auto_fetch_product_info(tool_name, tool_type="software"):
    info = {"Name": tool_name, "Type": tool_type}
    log = {"tool": tool_name, "type": tool_type, "sources": {}, "filled_fields": []}
    # 1. Wikipedia summary
    try:
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{tool_name.replace(' ', '_')}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("extract"):
                info["Description"] = data.get("extract")
                log["sources"]["Description"] = "Wikipedia"
            if data.get("content_urls", {}).get("desktop", {}).get("page"):
                info["Official Site"] = data.get("content_urls", {}).get("desktop", {}).get("page")
                log["sources"]["Official Site"] = "Wikipedia"
    except Exception:
        pass
    # 2. Try to scrape the official site for more info
    homepage = info.get("Official Site")
    if homepage:
        try:
            res = requests.get(homepage, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Try to get a better description
                if not info.get("Description"):
                    desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    if desc_tag and isinstance(desc_tag, Tag) and desc_tag.has_attr('content'):
                        info["Description"] = desc_tag['content']
                        log["sources"]["Description"] = "Official Site"
                # Try to get versions/models
                text = soup.get_text(separator='\n')
                versions = re.findall(r'Version[s]?:?\s*([\w\d\.,\- ]+)', text, re.IGNORECASE)
                if versions:
                    info["Versions"] = versions[0]
                    log["sources"]["Versions"] = "Official Site"
                # Try to get compatibility/platforms
                platforms = re.findall(r'(Windows|macOS|Linux|Android|iOS)', text, re.IGNORECASE)
                if platforms:
                    info["Compatibility"] = ', '.join(sorted(set([p.capitalize() for p in platforms])))
                    log["sources"]["Compatibility"] = "Official Site"
                # Try to get key features (look for <ul> or <li> under a features section)
                features = []
                for ul in soup.find_all('ul'):
                    prev_h2 = ul.find_previous('h2')
                    if prev_h2 and isinstance(prev_h2, Tag) and 'feature' in prev_h2.get_text().lower():
                        if isinstance(ul, Tag):
                            features.extend([li.get_text(strip=True) for li in ul.find_all('li') if isinstance(li, Tag)])
                if features:
                    info["Key Features"] = ', '.join(features)
                    log["sources"]["Key Features"] = "Official Site"
                # For hardware, try to get price, color options, where to buy, accessories
                if tool_type == "hardware":
                    price = re.findall(r'\$[0-9]+(?:\.[0-9]{2})?', text)
                    if price:
                        info["Price Range"] = ', '.join(sorted(set(price)))
                        log["sources"]["Price Range"] = "Official Site"
                    colors = re.findall(r'(Black|White|Red|Blue|Green|Yellow|Silver|Gray|Grey|Pink|Purple|Orange|Gold)', text, re.IGNORECASE)
                    if colors:
                        info["Color Options"] = ', '.join(sorted(set([c.capitalize() for c in colors])))
                        log["sources"]["Color Options"] = "Official Site"
                    buy_links = [a['href'] for a in soup.find_all('a', href=True) if isinstance(a, Tag) and isinstance(a.get('href'), str) and any(x in a['href'] for x in ['buy', 'shop', 'store', 'amazon', 'bestbuy', 'purchase'])]
                    buy_links = [link for link in buy_links if isinstance(link, str)]
                    if buy_links:
                        info["Where to Buy"] = ', '.join(sorted(set(buy_links)))
                        log["sources"]["Where to Buy"] = "Official Site"
                    acc = re.findall(r'(accessor(?:y|ies))[:\s]*([\w\d\.,\- ]+)', text, re.IGNORECASE)
                    if acc:
                        info["Accessories"] = ', '.join([a[1] for a in acc if a[1]])
                        log["sources"]["Accessories"] = "Official Site"
        except Exception:
            pass
    # 3. If a GitHub repo is detected, use GitHub API for releases
    github_url = None
    if homepage and 'github.com' in homepage:
        github_url = homepage
    if not github_url:
        try:
            resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{tool_name.replace(' ', '_')}")
            if resp.status_code == 200:
                data = resp.json()
                extlinks = data.get('content_urls', {})
                if extlinks:
                    for k, v in extlinks.items():
                        if isinstance(v, dict) and 'github.com' in v.get('page', ''):
                            github_url = v['page']
        except Exception:
            pass
    if github_url and tool_type == "software":
        try:
            m = re.match(r'https?://github.com/([^/]+)/([^/]+)', github_url)
            if m:
                owner, repo = m.group(1), m.group(2)
                api_url = f'https://api.github.com/repos/{owner}/{repo}/releases'
                resp = requests.get(api_url)
                if resp.status_code == 200:
                    releases = resp.json()
                    if releases and isinstance(releases, list):
                        tags = [r.get('tag_name') for r in releases if isinstance(r, dict) and r.get('tag_name')]
                        tags = [t for t in tags if t is not None]
                        if tags:
                            info["Versions"] = ', '.join(tags[:5])
                            log["sources"]["Versions"] = "GitHub"
        except Exception:
            pass
    # Fill missing fields with N/A
    if tool_type == "software":
        for field in ["Description", "Official Site", "Versions", "Compatibility", "Key Features", "Support/Reviews"]:
            if field not in info:
                info[field] = "N/A"
            else:
                log["filled_fields"].append(field)
    else:
        for field in ["Description", "Official Site", "Versions", "Price Range", "Color Options", "Compatibility", "Accessories", "Key Features", "Where to Buy", "Support/Reviews"]:
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

if __name__ == "__main__":
    # --- Main Tool Classification Flow ---
    tool_name_input = input("Enter the name of a package or any other software/tool to fetch metadata: ").strip()
    canonical_tool_key, specific_package = resolve_tool_name_and_specific_package(tool_name_input)
    if canonical_tool_key:
        use_case, tool_type = TOOL_CLASSIFICATION[canonical_tool_key]
        tool_name = canonical_tool_key  # Use canonical name for reporting/fetching
    else:
        tool_name = tool_name_input
        use_case = input("Enter use case: ").strip()
        tool_type = input("Enter type (software/hardware): ").strip().lower()
        specific_package = tool_name_input
    # --- Automated Info Fetching and Export ---
    if tool_type == "software" and use_case in TECHNICAL_USE_CASES:
        # Use technical report format
        print(f"[INFO] Using technical report format for {tool_name_input} ({use_case})")
        # --- FORCE GENERIC FETCHER FOR DEBUGGING ---
        metadata = fetch_generic_tool_metadata(specific_package)
        if metadata is None:
            print(f"[ERROR] No metadata found for {specific_package}. Skipping.")
            exit(1)
        # --- END FORCE ---
        organized = organize_metadata_for_output(metadata, use_case)
        output_dir = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{tool_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(organized, f, ensure_ascii=False, indent=2)
        print(f"Saved technical metadata to {output_path}")
        json_to_professional_word(output_path)
        # Export to PDF
        try:
            from docx2pdf import convert
            docx_path = os.path.join('SampleOutputs', 'docs', f"{tool_name}.docx")
            pdf_path = docx_path.replace('.docx', '.pdf')
            convert(docx_path, pdf_path)
            print(f"Exported PDF to {pdf_path}")
        except ImportError:
            print("docx2pdf not installed. Skipping PDF export.")
        except Exception as e:
            print(f"PDF export failed: {e}")
    else:
        # Use product info format
        print(f"[INFO] Using product info format for {tool_name_input} ({use_case})")
        info = auto_fetch_product_info(tool_name, tool_type)
        output_dir = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{tool_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"Saved product info to {output_path}")
        export_product_docx(output_path)
        # Export to PDF
        try:
            from docx2pdf import convert
            docx_path = os.path.join('SampleOutputs', 'docs', f"{tool_name}.docx")
            pdf_path = docx_path.replace('.docx', '.pdf')
            convert(docx_path, pdf_path)
            print(f"Exported PDF to {pdf_path}")
        except ImportError:
            print("docx2pdf not installed. Skipping PDF export.")
        except Exception as e:
            print(f"PDF export failed: {e}")
    exit(0) 