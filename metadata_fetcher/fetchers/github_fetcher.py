from metadata_fetcher import PackageMetadata
import requests
from urllib.parse import urlparse

RAW_GITHUB_PREFIX = "https://raw.githubusercontent.com"
GITHUB_API_PREFIX = "https://api.github.com/repos/"

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
    Given a PackageMetadata object with github_url, fetch and fill readme_content and requirements fields,
    and enrich with GitHub API data (stars, forks, issues, license, topics, etc.).
    """
    if not metadata.github_url:
        return metadata
    owner_repo = extract_github_repo_path(metadata.github_url)
    if not owner_repo:
        return metadata
    # Fetch README
    metadata.readme_content = fetch_readme_from_github(owner_repo)
    # Try requirements.txt from both main and master
    for branch in ["main", "master"]:
        if not metadata.requirements:
            req_url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/{branch}/requirements.txt"
            metadata.requirements = try_fetch_text(req_url)
        if metadata.requirements:
            break
    # --- GitHub API enrichment ---
    api_url = f"{GITHUB_API_PREFIX}{owner_repo}"
    try:
        repo_resp = requests.get(api_url, timeout=10)
        if repo_resp.status_code == 200:
            repo_data = repo_resp.json()
            metadata.stars = repo_data.get("stargazers_count")
            metadata.forks = repo_data.get("forks_count")
            metadata.open_issues = repo_data.get("open_issues_count")
            metadata.watchers = repo_data.get("subscribers_count")
            metadata.license = repo_data.get("license", {}).get("name") if repo_data.get("license") else metadata.license
            metadata.license_url = repo_data.get("license", {}).get("url") if repo_data.get("license") else metadata.license_url
            metadata.logo_url = repo_data.get("owner", {}).get("avatar_url")
            metadata.project_status = "archived" if repo_data.get("archived") else metadata.project_status
            metadata.topics = repo_data.get("topics", [])
            metadata.homepage = repo_data.get("homepage") or metadata.homepage
            metadata.author = repo_data.get("owner", {}).get("login") or metadata.author
            # Community profile
            community_url = f"{api_url}/community/profile"
            comm_resp = requests.get(community_url, timeout=10)
            if comm_resp.status_code == 200:
                comm_data = comm_resp.json()
                if comm_data.get("files"):
                    files = comm_data["files"]
                    metadata.contributing_url = files.get("contributing", {}).get("html_url") or metadata.contributing_url
                    metadata.code_of_conduct_url = files.get("code_of_conduct", {}).get("html_url") or metadata.code_of_conduct_url
            # Releases
            releases_url = f"{api_url}/releases"
            rel_resp = requests.get(releases_url, timeout=10)
            if rel_resp.status_code == 200:
                rel_data = rel_resp.json()
                for release in rel_data:
                    tag = release.get("tag_name")
                    date = release.get("published_at")
                    if tag and date:
                        if not metadata.release_dates:
                            metadata.release_dates = {}
                        metadata.release_dates[tag] = date
            # Community/support links (if available)
            if repo_data.get("html_url"):
                metadata.community_links["GitHub"] = repo_data["html_url"]
            if repo_data.get("homepage"):
                metadata.community_links["Homepage"] = repo_data["homepage"]
    except Exception:
        pass
    return metadata 