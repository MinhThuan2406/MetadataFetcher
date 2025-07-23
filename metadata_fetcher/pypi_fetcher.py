import requests
from packaging.version import parse as parse_version

PYPI_API_URL = "https://pypi.org/pypi/{}/json"

def fetch_pypi_metadata(app_name: str):
    """
    Fetch metadata for a given Python package from PyPI.
    Returns a dict with description, versions, dependencies, and project URLs.
    """
    result = {
        "description": None,
        "latest_version": None,
        "popular_versions": [],
        "dependencies": {},
        "info": {},
        "releases": {},
        "project_urls": {},
    }
    try:
        res = requests.get(PYPI_API_URL.format(app_name), timeout=10)
        if res.status_code != 200:
            return result
        data = res.json()
        info = data.get("info", {})
        releases = data.get("releases", {})
        result["info"] = info
        result["releases"] = releases
        result["description"] = info.get("summary") or info.get("description")
        all_versions = sorted(releases.keys(), key=parse_version, reverse=True)
        result["latest_version"] = all_versions[0] if all_versions else None
        result["popular_versions"] = all_versions[:3]
        for version in result["popular_versions"]:
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
            result["dependencies"][version] = dep_list
        result["project_urls"] = info.get("project_urls", {})
    except Exception:
        pass
    return result 