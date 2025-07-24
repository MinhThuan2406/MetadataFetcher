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

DOC_KEYWORDS = ["docs", "documentation", "install", "setup", "getting-started", "guide"]
INSTALL_KEYWORDS = ["install", "setup", "getting-started", "quickstart", "start"]

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

def fetch_generic_tool_metadata(app_name: str, homepage_override: Optional[str] = None) -> Optional[PackageMetadata]:
    # Use manual override if provided
    homepage = homepage_override or google_search(f"{app_name} official site")
    if not homepage or not validate_homepage(homepage, app_name):
        print(f"[WARN] Homepage validation failed for '{app_name}'. Please provide a manual override if needed.")
        return None
    homepage_html = fetch_html(homepage)
    documentation_links = find_links(homepage, DOC_KEYWORDS)
    installation_links = find_links(homepage, INSTALL_KEYWORDS)
    documentation = documentation_links[0] if documentation_links else None
    documentation_html = fetch_html(documentation) if documentation else None
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
    "Creative and Media Tools": ["Blender", "GIMP", "Elgato Stream deck", "ComfyUI"],
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

if __name__ == "__main__":
    tool_name = input("Enter the name of a package or any other software/tool to fetch metadata: ").strip()
    # print("Note: PyPI (Python Package Index) is the official repository for Python packages. If you enter a PyPI package name, the tool will fetch metadata directly from PyPI. For other software/tools, it will use web and documentation sources.")
    homepage_override = input("(Optional) Enter homepage override URL (or leave blank): ").strip() or None
    print("Select the use case for this tool:")
    for idx, uc in enumerate(USE_CASES, 1):
        print(f"  {idx}. {uc}")
    use_case_idx = input(f"Enter the number (1-{len(USE_CASES)}): ").strip()
    try:
        use_case = USE_CASES[int(use_case_idx)-1]
    except Exception:
        use_case = "Unspecified"

    # Try PyPI fetch first
    metadata = fetch_package_metadata(tool_name)
    is_pypi = metadata is not None and getattr(metadata, 'source', None) == "pypi"
    if metadata and (is_pypi and is_likely_real_pypi(metadata)):
        organized = organize_metadata_for_output(metadata, use_case)
        print("\n--- General Info ---")
        for k, v in organized["General Info"].items():
            print(f"{k}: {v}")
        print("\n--- Documentation ---")
        for k, v in organized["Documentation"].items():
            print(f"{k}: {v}")
        print("\n--- Installation ---")
        for k, v in organized["Installation"].items():
            print(f"{k}: {v}")
        print("\n--- Other Links ---")
        for k, v in organized["Other Links"].items():
            print(f"{k}: {v}")
        save = input("Save this metadata as JSON in SampleOutputs/? (y/n): ").strip().lower()
        if save == 'y':
            output_path = f"SampleOutputs/metadata/Non-PyPI/{tool_name}.json" if getattr(metadata, 'source', None) != 'pypi' else f"SampleOutputs/metadata/PyPI/{tool_name}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(organized, f, ensure_ascii=False, indent=2)
            print(f"Saved summary metadata to {output_path}")
    else:
        metadata = fetch_generic_tool_metadata(tool_name, homepage_override)
        if metadata:
            organized = organize_metadata_for_output(metadata, use_case)
            print("\n--- General Info ---")
            for k, v in organized["General Info"].items():
                print(f"{k}: {v}")
            print("\n--- Documentation ---")
            for k, v in organized["Documentation"].items():
                print(f"{k}: {v}")
            print("\n--- Installation ---")
            for k, v in organized["Installation"].items():
                print(f"{k}: {v}")
            print("\n--- Other Links ---")
            for k, v in organized["Other Links"].items():
                print(f"{k}: {v}")
            save = input("Save this metadata as JSON in SampleOutputs/? (y/n): ").strip().lower()
            if save == 'y':
                output_path = f"SampleOutputs/metadata/Non-PyPI/{tool_name}.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(organized, f, ensure_ascii=False, indent=2)
                print(f"Saved summary metadata to {output_path}")
        else:
            print("No metadata found for the given tool.") 