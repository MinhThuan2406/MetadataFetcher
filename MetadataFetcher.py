import requests
from packaging.version import parse as parse_version
from urllib.parse import urlparse
import re

PYPI_API_URL = "https://pypi.org/pypi/{}/json"
RAW_GITHUB_PREFIX = "https://raw.githubusercontent.com"

def fetch_package_metadata(app_name: str):
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

        # 3. Dependencies for top versions
        for version in result["popular_versions"]:
            try:
                deps = data["releases"].get(version, [])
                requires_dist = info.get("requires_dist", [])  # fallback
                if deps:
                    dep_info = deps[0].get("requires_dist", requires_dist)
                else:
                    dep_info = requires_dist
                result["dependencies"][version] = dep_info or []
            except Exception as e:
                result["dependencies"][version] = []
                print(f"[WARN] Couldn't parse deps for {version}: {e}")

        # 4. GitHub URL extraction
        project_url = info.get("project_url") or info.get("home_page") or ""
        urls = list(info.get("project_urls", {}).values()) + [project_url]
        github_links = [url for url in urls if "github.com" in (url or "")]
        if github_links:
            result["github_url"] = github_links[0]

        # 5. If GitHub found → fetch README & requirements
        if result["github_url"]:
            owner_repo = extract_github_repo_path(result["github_url"])
            if owner_repo:
                readme_url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/master/README.md"
                req_url = f"{RAW_GITHUB_PREFIX}/{owner_repo}/master/requirements.txt"

                result["readme_content"] = try_fetch_text(readme_url)
                result["requirements"] = try_fetch_text(req_url)

    except Exception as ex:
        print(f"[ERROR] Unexpected error: {ex}")

    return result


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


# ---- TESTING ----
if __name__ == "__main__":
    import json
    pkg = input("Nhập tên module/app/package: ").strip()
    metadata = fetch_package_metadata(pkg)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
