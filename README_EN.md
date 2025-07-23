## Overall Objective
Write a function that collects detailed information about any app/module/package (e.g., `"numpy"`) from popular sources like PyPI and GitHub, to support the development of a technical chatbot.

---

## Main Features

| Requirement            | Detailed Description                                                                |
|------------------------|-----------------------------------------------------------------------------------|
| Access PyPI            | Use the API https://pypi.org/pypi/<package>/json to fetch metadata                 |
| Get description        | Retrieve the summary or description of the package from PyPI                       |
| Get versions           | Get the list of versions (sorted in descending order)                              |
| Identify popular versions | Take the 3 most recent versions as "popular versions"                        |
| Get dependencies       | From each version's metadata or from requires_dist                                 |
| Identify GitHub repo   | If available, extract the GitHub URL from PyPI metadata (home_page, project_urls)  |
| Crawl GitHub (if any)  | Fetch README.md and requirements.txt from the GitHub repo (branch master/main)     |
| Return standard object | Include all the above information in a dict or JSON object                         |

---

## Input

```python
fetch_package_metadata(app_name: str)
# app_name: The name of a package from PyPI (e.g., "flask", "numpy", "langchain", ...)
```

---

## Output

```python
{
    "description": str,
    "latest_version": str,
    "popular_versions": List[str],
    "dependencies": Dict[str, List[str]],
    "github_url": str or None,
    "readme_content": str or None,
    "requirements": str or None
}
```

---

## Detailed Requirements & Expectations

| Item                   | Details                                                                              |
|------------------------|-------------------------------------------------------------------------------------|
| Intended use           | Integrate into a technical chatbot to help answer user questions about packages       |
| Future extensibility   | Should be extendable to answer: "What is this package for?", "Which version to use?", etc. |
| Data sources           | PyPI (metadata, versions, dependencies), GitHub (readme, requirements)               |
| Robustness             | If no GitHub or file not found → return None, do not raise errors                    |
| Skills to practice     | Working with APIs, merging data from multiple sources, cleaning/standardizing data, extensible code |

---

## Checklist

- [x] Can fetch description and versions from PyPI
- [x] Can get dependencies for main versions
- [x] Can identify GitHub repo if available
- [x] Can fetch README.md and requirements.txt if repo exists
- [x] Handles fallback if file or link is missing
- [x] Can run `fetch_package_metadata("numpy")` and see results
- [x] Code is clear, modular, easy to debug/extend

--- 
