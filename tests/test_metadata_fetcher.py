import sys
# DEPRECATED: This test uses old modules that no longer exist
# from metadata import fetch_package_metadata
# from metadata.fetchers.generic_fetcher import fetch_generic_tool_metadata

TEST_NAMES = [
    "flask",        # PyPI
    "numpy",        # PyPI
    "milvus",       # non-PyPI
    "postgresql",   # non-PyPI
    "redis",        # non-PyPI
    "requests",     # PyPI
]

def print_metadata(metadata, method):
    print(f"\n=== {metadata.name} ({method}) ===")
    print(f"Source: {metadata.source}")
    print(f"Description: {getattr(metadata, 'description', None)}")
    print(f"Homepage: {getattr(metadata, 'homepage', None)}")
    print(f"Documentation: {getattr(metadata, 'documentation', None)}")
    print(f"Latest Version: {getattr(metadata, 'latest_version', None)}")
    print(f"Popular Versions: {getattr(metadata, 'popular_versions', None)}")
    print(f"Dependencies: {getattr(metadata, 'dependencies', None)}")
    print(f"GitHub URL: {getattr(metadata, 'github_url', None)}")
    print(f"Installation: {getattr(metadata, 'installation', None)}")
    print(f"Documentation Links: {getattr(metadata, 'documentation_links', None)}")
    print(f"Installation Links: {getattr(metadata, 'installation_links', None)}")
    print("-----------------------------")

def main():
    for name in TEST_NAMES:
        print(f"\n>>> Testing '{name}'...")
        metadata = fetch_package_metadata(name)
        if metadata:
            print_metadata(metadata, method="PyPI API")
        else:
            metadata = fetch_generic_tool_metadata(name)
            if metadata:
                print_metadata(metadata, method="Manual + Google")
            else:
                print(f"No metadata found for '{name}'.")

if __name__ == "__main__":
    main() 