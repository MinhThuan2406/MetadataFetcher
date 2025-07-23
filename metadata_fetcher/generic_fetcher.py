from metadata_fetcher.schema import PackageMetadata, InstallationInfo
from metadata_fetcher.google_search import google_search
from metadata_fetcher.installation_parser import extract_installation_commands
from typing import Optional, List
import requests
from bs4 import BeautifulSoup, Tag
import re
import json
import os

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
        return links
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
    install_htmls = [fetch_html(link) for link in installation_links[:3] if link]
    install_cmds = [extract_installation_commands(html) for html in install_htmls if html]
    def pick_first(attr):
        for cmd in install_cmds:
            val = getattr(cmd, attr, None)
            if val:
                return val
        return None
    installation = InstallationInfo(
        pip=pick_first('pip'),
        docker=pick_first('docker'),
        from_source=pick_first('from_source'),
        other=pick_first('other')
    )
    if not (installation.pip or installation.docker or installation.from_source or installation.other):
        installation = extract_installation_commands(documentation_html) if documentation_html else extract_installation_commands(homepage_html)
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
    os.makedirs("SampleOutputs", exist_ok=True)
    output_path = os.path.join("SampleOutputs", f"{tool_name}_metadata.json")
    # Create a summary dict similar to the terminal output
    summary = {
        "Name": metadata.name,
        "Homepage": metadata.homepage,
        "Documentation": metadata.documentation,
        "Source": metadata.source,
        "Homepage HTML length": len(metadata.homepage_html) if metadata.homepage_html else 0,
        "Documentation HTML length": len(metadata.documentation_html) if metadata.documentation_html else 0,
        "Documentation Links": metadata.documentation_links[:5] + (["..."] if len(metadata.documentation_links) > 5 else []),
        "Installation Links": metadata.installation_links[:5] + (["..."] if len(metadata.installation_links) > 5 else []),
        "Installation (pip)": metadata.installation.pip,
        "Installation (docker)": metadata.installation.docker,
        "Installation (from_source)": metadata.installation.from_source,
        "Installation (other)": metadata.installation.other,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        import json
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved summary metadata to {output_path}")

if __name__ == "__main__":
    tool_name = input("Enter a non-PyPI tool name to fetch metadata (e.g., milvus, postgresql): ").strip()
    homepage_override = input("(Optional) Enter homepage override URL (or leave blank): ").strip() or None
    metadata = fetch_generic_tool_metadata(tool_name, homepage_override)
    if metadata:
        print("\nFetched Metadata:")
        print(f"Name: {metadata.name}")
        print(f"Homepage: {metadata.homepage}")
        print(f"Documentation: {metadata.documentation}")
        print(f"Source: {metadata.source}")
        print(f"Homepage HTML length: {len(metadata.homepage_html) if metadata.homepage_html else 0}")
        print(f"Documentation HTML length: {len(metadata.documentation_html) if metadata.documentation_html else 0}")
        print(f"Documentation Links: {metadata.documentation_links}")
        print(f"Installation Links: {metadata.installation_links}")
        print(f"Installation (pip): {metadata.installation.pip}")
        print(f"Installation (docker): {metadata.installation.docker}")
        print(f"Installation (from_source): {metadata.installation.from_source}")
        print(f"Installation (other): {metadata.installation.other}")
        save = input("Save this metadata as JSON in SampleOutputs/? (y/n): ").strip().lower()
        if save == 'y':
            save_metadata_json(metadata, tool_name)
    else:
        print("No metadata found for the given tool.") 