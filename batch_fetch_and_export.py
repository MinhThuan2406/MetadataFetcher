import os
import json
from metadata_fetcher.generic_fetcher import TOOL_CLASSIFICATION, normalize_tool_name, auto_fetch_product_info
from export_to_word import export_product_docx

try:
    from docx2pdf import convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False

# Hardcoded list of tools for batch processing (can be replaced with file input)
BATCH_TOOL_LIST = [
    "Python", "PyTorch", "TensorFlow", "Anaconda", "Pandas", "JupyterLab / Jupyter Notebook", "R",
    "Blender", "GIMP", "Elgato Stream deck", "ComfyUI",
    "Visual Studio Code", "Git (Version Control)", "Pycharm", "GitHub Desktop",
    "LangChain", "Ollama", "Hugging Face Transformers"
]

# Key fields to check for manual review
KEY_FIELDS_SOFTWARE = ["Description", "Official Site", "Versions"]
KEY_FIELDS_HARDWARE = ["Description", "Official Site", "Versions", "Price Range", "Where to Buy"]

manual_review = []

for tool_name_input in BATCH_TOOL_LIST:
    tool_name = normalize_tool_name(tool_name_input)
    use_case, tool_type = TOOL_CLASSIFICATION.get(tool_name, (None, None))
    if not use_case or not tool_type:
        print(f"[WARN] Tool '{tool_name_input}' not classified. Skipping.")
        continue
    print(f"Processing: {tool_name_input} ({use_case}, {tool_type})")
    info = auto_fetch_product_info(tool_name, tool_type)
    # Save as JSON
    output_dir = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{tool_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    # Export to DOCX
    export_product_docx(output_path)
    # Export to PDF
    docx_path = os.path.join('SampleOutputs', 'docs', f"{tool_name}.docx")
    pdf_path = docx_path.replace('.docx', '.pdf')
    if DOCX2PDF_AVAILABLE:
        try:
            convert(docx_path, pdf_path)
            print(f"Exported PDF to {pdf_path}")
        except Exception as e:
            print(f"PDF export failed for {tool_name}: {e}")
    else:
        print("docx2pdf not installed. Skipping PDF export.")
    # Check for missing key fields
    key_fields = KEY_FIELDS_SOFTWARE if tool_type == "software" else KEY_FIELDS_HARDWARE
    missing = [field for field in key_fields if info.get(field, "N/A") == "N/A"]
    if missing:
        manual_review.append((tool_name_input, missing))

print("\nBatch processing complete.")
if manual_review:
    print("\nTools needing manual review (missing key fields):")
    for tool, fields in manual_review:
        print(f"- {tool}: missing {', '.join(fields)}")
else:
    print("All tools have key fields filled.") 