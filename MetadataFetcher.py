import requests
from packaging.version import parse as parse_version
from urllib.parse import urlparse
import re

PYPI_API_URL = "https://pypi.org/pypi/{}/json"
RAW_GITHUB_PREFIX = "https://raw.githubusercontent.com"


def fetch_package_metadata(app_name: str):
    """
    Fetch detailed metadata for a given Python package from PyPI and GitHub (if available).
    Returns a dict with description, versions, dependencies, GitHub URL, README, and requirements.
    """
    result = {
        "description": None,
        "latest_version": None,
        "popular_versions": [],
        "dependencies": {},
        "github_url": None,
        "readme_content": None,
        "requirements": None
    }

    try:
        # 1. Fetch PyPI metadata
        res = requests.get(PYPI_API_URL.format(app_name), timeout=10)
        if res.status_code != 200:
            print(f"[ERROR] Package '{app_name}' not found on PyPI.")
            return result

        data = res.json()
        info = data.get("info", {})
        releases = data.get("releases", {})

        # 2. Description & version info
        result["description"] = info.get("summary") or info.get("description")
        all_versions = sorted(releases.keys(), key=parse_version, reverse=True)
        result["latest_version"] = all_versions[0] if all_versions else None
        result["popular_versions"] = all_versions[:3]

        # 3. Dependencies for top versions (prefer release metadata, fallback to info)
        for version in result["popular_versions"]:
            dep_list = []
            try:
                # Try to get requires_dist from release metadata (if available)
                release_files = releases.get(version, [])
                found = False
                for file_info in release_files:
                    # Some distributions may have 'requires_dist' in their metadata
                    if 'requires_dist' in file_info and file_info['requires_dist']:
                        dep_list = file_info['requires_dist']
                        found = True
                        break
                if not found:
                    # Fallback: try to get from info (may only reflect latest version)
                    dep_list = info.get("requires_dist", []) or []
            except Exception as e:
                print(f"[WARN] Couldn't parse deps for {version}: {e}")
                dep_list = []
            result["dependencies"][version] = dep_list

        # 4. GitHub URL extraction
        project_url = info.get("project_url") or info.get("home_page") or ""
        urls = list(info.get("project_urls", {}).values()) + [project_url]
        github_links = [url for url in urls if url and "github.com" in url]
        if github_links:
            result["github_url"] = github_links[0]

        # 5. If GitHub found → fetch README & requirements (try both 'main' and 'master')
        if result["github_url"]:
            owner_repo = extract_github_repo_path(result["github_url"])
            if owner_repo:
                # Fetch README using the robust helper
                result["readme_content"] = fetch_readme_from_github(owner_repo)
                # Try requirements.txt as before
                for branch in ["main", "master"]:
                    if not result["requirements"]:
                        req_url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/{branch}/requirements.txt"
                        result["requirements"] = try_fetch_text(req_url)
                    if result["requirements"]:
                        break

    except Exception as ex:
        print(f"[ERROR] Unexpected error: {ex}")

    return result


def extract_github_repo_path(github_url: str):
    """
    Extract the owner/repo path from a GitHub URL.
    """
    try:
        parts = urlparse(github_url)
        path_parts = parts.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return f"{path_parts[0]}/{path_parts[1]}"
    except Exception:
        pass
    return None


def try_fetch_text(url: str):
    """
    Try to fetch the text content from a URL. Return None if not found or error.
    """
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


def fetch_readme_from_github(owner_repo):
    """
    Try to fetch the README file from GitHub, covering common names and extensions (case-insensitive).
    Returns the content if found, else None.
    """
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


# ---- TESTING ----
if __name__ == "__main__":
    def filter_readme_lines(readme_content, max_lines=None):
        """
        Filter out badge, logo, image, and reST/Markdown directive lines from README content.
        If max_lines is set, return only that many lines. Otherwise, return all meaningful lines.
        """
        if not readme_content:
            return []
        lines = readme_content.splitlines()
        filtered = []
        for line in lines:
            l = line.strip()
            # Skip empty lines, html tags, badges, images, markdown links, and reST directives
            if not l:
                continue
            if l.startswith("<") and l.endswith(">"):
                continue
            if l.startswith("![") or l.startswith("<img"):
                continue
            if "badge" in l.lower() or "logo" in l.lower():
                continue
            if l.startswith("[!") and "](" in l:
                continue
            if l.startswith("#") and len(l) <= 3:  # skip single # or ##
                continue
            if l.startswith(".."):  # skip reST directives and comments
                continue
            if l.startswith(":") and ":" in l[1:]:  # skip reST field lists
                continue
            filtered.append(line)
            if max_lines and len(filtered) >= max_lines:
                break
        return filtered

    def pretty_print_metadata(metadata):
        print(f"\nPackage: {pkg}")
        print(f"Description: {metadata['description'] or 'No description found.'}\n")
        print(f"Latest Version: {metadata['latest_version'] or 'Unknown'}")
        if metadata['popular_versions']:
            print(f"Popular Versions: {', '.join(metadata['popular_versions'])}")
        else:
            print("Popular Versions: None found.")
        print("\nDependencies:")
        for ver in metadata['popular_versions']:
            deps = metadata['dependencies'].get(ver)
            if deps:
                print(f"  - {ver}: {', '.join(deps)}")
            else:
                print(f"  - {ver}: None")
        print(f"\nGitHub URL: {metadata['github_url'] or 'No GitHub URL found.'}")
        print("\nREADME:")
        if metadata['readme_content']:
            filtered_lines = filter_readme_lines(metadata['readme_content'], max_lines=None)
            if filtered_lines:
                for line in filtered_lines:
                    print(f"  {line}")
            else:
                print("  No meaningful content found in README.")
        else:
            print("  No README found.")
        print("\nRequirements.txt:")
        if metadata['requirements']:
            print(metadata['requirements'])
        else:
            print("  No requirements.txt found.")

    pkg = input("Input the module/app/package name: ").strip()
    metadata = fetch_package_metadata(pkg)
    pretty_print_metadata(metadata)
