# MetadataFetcher - Quick Start Commands

After the massive codebase update, here are the **correct commands** to fetch tool metadata:

## 🚀 Primary Commands (Recommended)

### Fetch Single Tool
```bash
# Basic fetch (JSON format)
python cli/main.py fetch <tool_name>

# Examples:
python cli/main.py fetch flask
python cli/main.py fetch numpy --format yaml
python cli/main.py fetch pandas --format docx
python cli/main.py fetch tensorflow --format pdf
```

### Fetch Multiple Tools (Batch)
```bash
# Batch processing
python cli/main.py batch flask numpy pandas
python cli/main.py batch --input-file tools.txt --format yaml
python cli/main.py batch redis postgresql mysql --format json
```

### System Information
```bash
# Show available formats
python cli/main.py formats

# Show system info
python cli/main.py info
```

## 📋 Available Options

### Output Formats
- `--format json` (default)
- `--format yaml`
- `--format docx`
- `--format pdf`

### Output Directory
- `--output-dir my_outputs`

### Tool Categories
- `--category ai_ml`
- `--category database`
- `--category web_framework`
- `--category data_science`
- `--category dev_tools`
- `--category creative_media`
- `--category system_tools`
- `--category other`

## 🎯 Real Examples

### AI/ML Tools
```bash
python cli/main.py fetch tensorflow --format json
python cli/main.py fetch pytorch --format yaml
python cli/main.py fetch scikit-learn --format docx
```

### Database Tools
```bash
python cli/main.py fetch postgresql --category database
python cli/main.py fetch redis --category database
python cli/main.py fetch mysql --category database
```

### Web Frameworks
```bash
python cli/main.py fetch flask --category web_framework
python cli/main.py fetch django --category web_framework
python cli/main.py fetch fastapi --category web_framework
```

### Batch Processing
```bash
python cli/main.py batch tensorflow pytorch scikit-learn --format json
python cli/main.py batch postgresql redis mysql --format yaml
python cli/main.py batch flask django fastapi --format docx
```

## 📁 Output Structure

Results are saved to:
```
outputs/
├── json/
├── yaml/
├── docx/
└── pdf/
```

## ⚠️ Important Notes

1. **Old commands are broken** - The legacy commands like `python -m metadata_fetcher.fetchers.generic_fetcher` no longer work
2. **Use the new CLI** - Always use `python cli/main.py` commands
3. **Multiple formats supported** - You can export to JSON, YAML, DOCX, or PDF
4. **Batch processing available** - Process multiple tools at once
5. **Caching enabled** - Results are cached for better performance

## 🧪 Testing

```bash
# Run demo
python examples/demo.py

# Run tests
python -m pytest tests/
```

## 📖 Help

```bash
# General help
python cli/main.py --help

# Command-specific help
python cli/main.py fetch --help
python cli/main.py batch --help
``` 