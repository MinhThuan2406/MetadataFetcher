from metadata_fetcher.schema import PackageMetadata, InstallationInfo
import requests
from packaging.version import parse as parse_version

PYPI_API_URL = "https://pypi.org/pypi/{}/json"

def fetch_pypi_metadata(app_name: str):
    """
    Fetch metadata for a given Python package from PyPI.
    Returns a PackageMetadata object.
    """
    try:
        res = requests.get(PYPI_API_URL.format(app_name), timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        info = data.get("info", {})
        releases = data.get("releases", {})
        description = info.get("summary") or info.get("description")
        all_versions = sorted(releases.keys(), key=parse_version, reverse=True)
        latest_version = all_versions[0] if all_versions else None
        popular_versions = all_versions[:3]
        dependencies = {}
        for version in popular_versions:
            dep_list = []
            try:
                release_files = releases.get(version, [])
                found = False
                for file_info in release_files:
                    if 'requires_dist' in file_info and file_info['requires_dist']:
                        dep_list = file_info['requires_dist']
                        found = True
                        break
                if not found:
                    dep_list = info.get("requires_dist", []) or []
            except Exception:
                dep_list = []
            dependencies[version] = dep_list
        project_url = info.get("project_url") or info.get("home_page") or ""
        urls = list(info.get("project_urls", {}).values()) + [project_url]
        github_url = None
        homepage = None
        documentation = None
        # Try to find documentation link in project_urls
        project_urls = info.get("project_urls", {})
        for key, url in project_urls.items():
            if key.lower() in ["documentation", "docs", "doc", "readthedocs"]:
                documentation = url
                break
        # Fallback: if homepage looks like documentation
        if not documentation:
            homepage_candidate = None
            for url in urls:
                if url and not homepage_candidate:
                    homepage_candidate = url
                if url and ("/doc" in url or "/docs" in url):
                    documentation = url
                    break
            if not documentation and homepage_candidate:
                homepage = homepage_candidate
            else:
                homepage = homepage_candidate
        else:
            # Set homepage to first non-doc url if possible
            homepage_candidate = None
            for url in urls:
                if url and url != documentation and not homepage_candidate:
                    homepage_candidate = url
            if homepage_candidate:
                homepage = homepage_candidate
        # Installation info (pip only for PyPI)
        installation = InstallationInfo(
            pip=f"pip install {app_name}"
        )
        return PackageMetadata(
            name=app_name,
            description=description,
            latest_version=latest_version,
            popular_versions=popular_versions,
            dependencies=dependencies,
            github_url=github_url,
            installation=installation,
            homepage=homepage,
            documentation=documentation,
            source="pypi"
        )
    except Exception:
        return None 