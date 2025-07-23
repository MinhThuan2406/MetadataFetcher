from metadata_fetcher import PackageMetadata
import requests
from urllib.parse import urlparse

RAW_GITHUB_PREFIX = "https://raw.githubusercontent.com"

def extract_github_repo_path(github_url: str):
    try:
        parts = urlparse(github_url)
        path_parts = parts.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return f"{path_parts[0]}/{path_parts[1]}"
    except Exception:
        pass
    return None

def try_fetch_text(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def fetch_readme_from_github(owner_repo):
    readme_names = [
        "README.md", "README.rst", "README.txt", "README",
        "readme.md", "readme.rst", "readme.txt", "readme",
        "ReadMe.md", "ReadMe.rst", "ReadMe.txt", "ReadMe"
    ]
    branches = ["main", "master"]
    for branch in branches:
        for name in readme_names:
            url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/{branch}/{name}"
            content = try_fetch_text(url)
            if content:
                return content
    return None

def enrich_with_github_data(metadata: PackageMetadata):
    """
    Given a PackageMetadata object with github_url, fetch and fill readme_content and requirements fields.
    """
    if not metadata.github_url:
        return metadata
    owner_repo = extract_github_repo_path(metadata.github_url)
    if not owner_repo:
        return metadata
    metadata.readme_content = fetch_readme_from_github(owner_repo)
    # Try requirements.txt from both main and master
    for branch in ["main", "master"]:
        if not metadata.requirements:
            req_url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/{branch}/requirements.txt"
            metadata.requirements = try_fetch_text(req_url)
        if metadata.requirements:
            break
    return metadata 