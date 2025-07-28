# Usage Examples

This document provides practical examples of how to use the MetadataFetcher system.

## 🚀 **Quick Start**

### **Single Tool Fetch**
```bash
# Fetch metadata for a single tool
python -m cli.main fetch pandas --format json

# Fetch with different output formats
python -m cli.main fetch numpy --format yaml
python -m cli.main fetch flask --format docx
python -m cli.main fetch matplotlib --format pdf
```

### **Batch Processing**
```bash
# Fetch multiple tools at once
python -m cli.main batch pandas numpy matplotlib --format json

# Process from file
echo "pandas\nnumpy\nmatplotlib" > tools.txt
python -m cli.main batch --input-file tools.txt --format yaml
```

## 📊 **Output Formats**

### **JSON Output**
```json
{
  "name": "pandas",
  "display_name": "pandas",
  "description": "Powerful data structures for data analysis...",
  "version": "2.1.4",
  "latest_version": "2.1.4",
  "category": "AI_ML",
  "homepage": "https://pandas.pydata.org",
  "documentation": "https://pandas.pydata.org/docs/",
  "repository": "https://github.com/pandas-dev/pandas",
  "license": "BSD-3-Clause",
  "author": "The pandas development team",
  "maintainer": null,
  "source_priority": "online"
}
```

### **YAML Output**
```yaml
name: pandas
display_name: pandas
description: Powerful data structures for data analysis...
version: "2.1.4"
latest_version: "2.1.4"
category: AI_ML
homepage: https://pandas.pydata.org
documentation: https://pandas.pydata.org/docs/
repository: https://github.com/pandas-dev/pandas
license: BSD-3-Clause
author: The pandas development team
maintainer: null
source_priority: online
```

### **DOCX/PDF Reports**
Professional reports with:
- Tool metadata summary
- Installation instructions
- Documentation links
- Repository information
- License details

## 🔧 **Advanced Usage**

### **Programmatic Usage**
```python
from metadata_fetcher.core import FetcherRegistry, FetcherConfig
from metadata_fetcher.core.pypi_fetcher import PyPIFetcher

# Setup
config = FetcherConfig()
registry = FetcherRegistry()
registry.register_fetcher(PyPIFetcher(config))

# Fetch metadata
metadata = registry.fetch("pandas")
if metadata:
    print(f"Found: {metadata.display_name}")
    print(f"Version: {metadata.version}")
    print(f"Description: {metadata.description}")
```

### **Custom Configuration**
```python
from metadata_fetcher.core import FetcherConfig

# Custom configuration
config = FetcherConfig(
    output_directory="custom_outputs",
    output_format="yaml",
    enable_caching=True,
    cache_ttl=3600
)
```

## 📁 **Output Organization**

### **Directory Structure**
```
outputs/
├── json/              # JSON metadata files
│   ├── pandas_20241201_143022.json
│   └── numpy_20241201_143025.json
├── yaml/              # YAML metadata files
│   ├── pandas_20241201_143022.yaml
│   └── numpy_20241201_143025.yaml
├── docs/              # DOCX report files
│   ├── pandas_20241201_143022.docx
│   └── numpy_20241201_143025.docx
└── pdf/               # PDF report files
    ├── pandas_20241201_143022.pdf
    └── numpy_20241201_143025.pdf
```

### **File Naming Convention**
- **Format**: `{tool_name}_{timestamp}.{format}`
- **Example**: `pandas_20241201_143022.json`
- **Timestamp**: YYYYMMDD_HHMMSS format

## 🎯 **Best Practices**

### **Efficient Batch Processing**
```bash
# Use batch processing for multiple tools
python -m cli.main batch tool1 tool2 tool3 --format json

# Process from file for large lists
python -m cli.main batch --input-file large_tool_list.txt --format yaml
```

### **Output Format Selection**
- **JSON/YAML**: For data processing and APIs
- **DOCX**: For human-readable reports
- **PDF**: For formal documentation

### **Caching Benefits**
- **Faster**: Cached responses reduce API calls
- **Reliable**: Reduces rate limiting issues
- **Efficient**: Automatic cache management

## 🔍 **Troubleshooting**

### **Common Issues**
1. **Tool not found**: Try different fetchers or check spelling
2. **Rate limiting**: Enable caching or increase delays
3. **Output errors**: Check directory permissions
4. **Format issues**: Verify dependencies installed

### **Debug Mode**
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python -m cli.main fetch pandas --format json
```

## 📚 **Next Steps**

- **Explore CLI**: Try all available commands
- **Check Examples**: Review reference files
- **Read Documentation**: Understand advanced features
- **Contribute**: Report issues or suggest improvements 