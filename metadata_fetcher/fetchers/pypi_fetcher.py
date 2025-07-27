from metadata_fetcher.schema import PackageMetadata, InstallationInfo
import requests
from packaging.version import parse as parse_version
from typing import Optional

PYPI_API_URL = "https://pypi.org/pypi/{}/json"

def fetch_pypi_metadata(app_name: str) -> Optional[PackageMetadata]:
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
        license = info.get("license")
        author = info.get("author")
        maintainer = info.get("maintainer")
        keywords = info.get("keywords")
        classifiers = info.get("classifiers", [])
        platforms = info.get("platform", None)
        # Extract project status from classifiers
        project_status = None
        for c in classifiers:
            if c.startswith("Development Status"):
                project_status = c
                break
        # Extract topics from keywords (comma-separated)
        topics = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
        # Extract release dates
        release_dates = {}
        for version, files in releases.items():
            if files:
                # Use upload_time_iso_8601 from the first file
                upload_time = files[0].get("upload_time_iso_8601")
                if upload_time:
                    release_dates[version] = upload_time
        # Extract project_urls
        project_urls = info.get("project_urls", {})
        changelog_url = project_urls.get("Changelog") or project_urls.get("Release Notes")
        api_reference_url = project_urls.get("API Reference")
        tutorials_url = project_urls.get("Tutorials")
        faq_url = project_urls.get("FAQ")
        contributing_url = project_urls.get("Contributing")
        code_of_conduct_url = project_urls.get("Code of Conduct")
        documentation = project_urls.get("Documentation") or documentation
        homepage = project_urls.get("Homepage") or homepage
        license_url = project_urls.get("License")
        # Try to find GitHub URL
        for key, url in project_urls.items():
            if "github.com" in str(url).lower():
                github_url = url
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
            pip=[{"command": f"pip install {app_name}"}]
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
            source="pypi",
            license=license,
            license_url=license_url,
            author=author,
            maintainer=maintainer,
            project_status=project_status,
            platforms=[platforms] if platforms else [],
            changelog_url=changelog_url,
            api_reference_url=api_reference_url,
            tutorials_url=tutorials_url,
            faq_url=faq_url,
            contributing_url=contributing_url,
            code_of_conduct_url=code_of_conduct_url,
            topics=topics,
            release_dates=release_dates
        )
    except Exception:
        return None 