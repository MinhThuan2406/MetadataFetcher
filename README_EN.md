# MetadataFetcher

**MetadataFetcher** is a tool for collecting detailed metadata about any package, module, app, or tool (including non-PyPI tools) from multiple sources such as PyPI, GitHub, Google Search, and official homepages. It returns installation guides, documentation links, README, dependencies, and more—ready for integration into technical chatbots or automation systems.

---

## 🚀 Features
- **Automatic metadata collection from PyPI, GitHub, Google Search**
- **Supports non-PyPI tools** (e.g., milvus, postgresql, redis, elastic, nats...)
- **Extracts installation instructions** (pip, docker, docker compose, build from source, package manager, etc.)
- **Finds and saves documentation/setup links**
- **Stores raw data (HTML/text) for deeper analysis**
- **Saves concise sample outputs as JSON files**

---

## 🛠️ Setup & Requirements
1. **Clone the repo**
2. **Install Python >= 3.8**
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** (do not commit to git!) with:
   ```
   GOOGLE_CSE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```
   > Register for a Google Custom Search API key and CSE ID as described below.

### 🔑 How to Get Google Custom Search API Key & CSE ID

1. **Get a Google API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project (if needed).
   - Go to **APIs & Services > Library**.
   - Search for **Custom Search API** and enable it.
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > API key**. Copy the key.

2. **Get a Google CSE ID:**
   - Go to [Google Custom Search Engine](https://cse.google.com/cse/all).
   - Click **Add** to create a new search engine.
   - For “Sites to search”, enter `*.io` or any domain (you can edit this later).
   - Click **Create**.
   - In the control panel, click the search engine name, then **Setup**.
   - Copy the **Search engine ID**.
   - To search the whole web, in the control panel, set “Sites to search” to “Search the entire web”.

3. **Add both values to your `.env` file:**
   ```
   GOOGLE_CSE_API_KEY=your_api_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   ```

---

## 💡 Quick Usage

> **Note:**
> - For **PyPI packages** (e.g., flask, numpy), use the Python API for the most complete metadata. The API provides accurate documentation links and installation info.
> - The CLI is best for **non-PyPI tools** (e.g., milvus, postgresql, redis). For PyPI packages, the CLI may not return full metadata and will warn you to use the API.

### 1. Fetch metadata for any PyPI package (recommended)
```python
from metadata_fetcher import fetch_package_metadata
metadata = fetch_package_metadata("flask")
print(metadata)
# The 'documentation' field and installation info will be set if available in PyPI metadata.
```

### 2. Fetch metadata for a non-PyPI tool or any tool (CLI)
```bash
python -m metadata_fetcher.generic_fetcher
# Enter the tool or package name when prompted (e.g., flask, milvus, postgresql)
# You can manually enter a homepage URL if Google returns the wrong one
```
> ⚠️ If you enter a PyPI package name in the CLI, you may see a warning suggesting to use the Python API for more complete results.

### 3. Save sample output as JSON
After running, choose to save the output when prompted. The file will be in the `SampleOutputs/metadata/PyPI/` or `SampleOutputs/metadata/Non-PyPI/` directory. The output is a concise summary JSON (see below).

---

## 📦 Output Schema (Standardized)
```python
{
  "name": str,
  "description": str | None,
  "latest_version": str | None,
  "popular_versions": List[str],
  "dependencies": Dict[str, List[str]],
  "github_url": str | None,
  "readme_content": str | None,
  "requirements": str | None,
  "installation": {
    "pip": List[dict],
    "from_source": List[dict],
    "docker": List[dict],
    "docker_compose": List[dict],
    "other": List[dict],
    "platforms": Dict[str, List[dict]]
  },
  "homepage": str | None,
  "documentation": str | None,
  "documentation_links": List[str],
  "installation_links": List[str],
  "homepage_html": str | None,
  "documentation_html": str | None,
  "source": "pypi" | "manual + google"
}
```
- **Note:** The saved JSON summary output is concise, showing only the most relevant fields and links, not the full verbose listing.

---

## 📋 Example Output (milvus)
```json
{
  "Name": "milvus",
  "Homepage": "https://milvus.io/",
  "Documentation": "https://milvus.io/docs",
  "Source": "manual + google",
  "Documentation Links": ["https://milvus.io/docs", ...],
  "Installation Summary": {
    "pip": {
      "command": "pip install -U pymilvus",
      "explanation": "Install a Python package using pip.",
      "note": "Run in your terminal or command prompt."
    },
    ...
  }
}
```

---

## 📖 Architecture & Extensibility
- **Modular:** Separate fetchers for PyPI, GitHub, Google, installation parser, etc.
- **Easy to extend:** Add new sources or parsers as needed
- **Ready for integration with chatbots, APIs, UIs, etc.**
- **Installation parser:** Recognizes pip, docker, docker compose, conda, npm, system package managers, and more, with explanations and platform hints.
- **Google Search:** Requires `.env` with API key and CSE ID; prints error if missing.
- **Dependencies:** `requests`, `packaging`, `beautifulsoup4`, `python-dotenv`.