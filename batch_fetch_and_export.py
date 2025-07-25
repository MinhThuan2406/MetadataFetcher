import os
import json
from metadata_fetcher.generic_fetcher import TOOL_CLASSIFICATION, normalize_tool_name, auto_fetch_product_info
from export_to_word import export_product_docx
from metadata_fetcher.creative_media_fetcher import fetch_creative_media_metadata, TOOL_FALLBACKS
from export_to_word import export_metadata_to_word

try:
    from docx2pdf import convert as docx2pdf_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False

# Hardcoded list of tools for batch processing (can be replaced with file input)
# BATCH_TOOL_LIST = [
#     "Python", "PyTorch", "TensorFlow", "Anaconda", "Pandas", "JupyterLab / Jupyter Notebook", "R",
#     "Blender", "GIMP", "Elgato Stream deck", "ComfyUI",
#     "Visual Studio Code", "Git (Version Control)", "Pycharm", "GitHub Desktop",
#     "LangChain", "Ollama", "Hugging Face Transformers"
# ]

BATCH_TOOL_LIST = [
    "Pandas"
]

# Key fields to check for manual review
KEY_FIELDS_SOFTWARE = ["Description", "Official Site", "Versions"]
KEY_FIELDS_HARDWARE = ["Description", "Official Site", "Versions", "Price Range", "Where to Buy"]

manual_review = []

def process_creative_media_tools():
    tools = list(TOOL_FALLBACKS.keys())
    for tool in tools:
        print(f"Processing: {tool}")
        meta = fetch_creative_media_metadata(tool)
        # Save as JSON
        output_dir = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, f"{tool}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            import json
            json.dump(meta, f, ensure_ascii=False, indent=2)
        # Export to DOCX
        docx_dir = os.path.join('SampleOutputs', 'docs', 'docx')
        os.makedirs(docx_dir, exist_ok=True)
        docx_path = os.path.join(docx_dir, f"{tool}.docx")
        export_metadata_to_word(meta, docx_path)
        # Export to PDF
        pdf_dir = os.path.join('SampleOutputs', 'docs', 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{tool}.pdf")
        if DOCX2PDF_AVAILABLE:
            try:
                docx2pdf_convert(docx_path, pdf_path)
                print(f"Exported PDF to {pdf_path}")
            except Exception as e:
                print(f"PDF export failed for {tool}: {e}")
        else:
            print("docx2pdf not installed. Skipping PDF export.")
    print("\nCreative/media tool batch processing complete.")


for tool_name_input in BATCH_TOOL_LIST:
    tool_name = normalize_tool_name(tool_name_input)
    use_case, tool_type = TOOL_CLASSIFICATION.get(tool_name, (None, None))
    if not use_case or not tool_type:
        print(f"[WARN] Tool '{tool_name_input}' not classified. Skipping.")
        continue
    print(f"Processing: {tool_name_input} ({use_case}, {tool_type})")
    info = auto_fetch_product_info(tool_name, tool_type)
    # Try to fill missing fields from JSON fallback
    json_fallback_path = os.path.join("SampleOutputs", "metadata", "Non-PyPI", f"{tool_name}.json")
    if os.path.exists(json_fallback_path):
        with open(json_fallback_path, "r", encoding="utf-8") as f:
            fallback_data = json.load(f)
        for k, v in fallback_data.items():
            if (k not in info or not info[k] or info[k] in ["N/A", "", None]) and v not in ["N/A", "", None]:
                info[k] = v
    # Save as JSON
    output_dir = os.path.join("SampleOutputs", "metadata", "Non-PyPI")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{tool_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    # Export to DOCX (to docs/docx/)
    docx_dir = os.path.join('SampleOutputs', 'docs', 'docx')
    os.makedirs(docx_dir, exist_ok=True)
    docx_path = os.path.join(docx_dir, f"{tool_name}.docx")
    export_product_docx(output_path)
    # Export to PDF (to docs/pdf/)
    pdf_dir = os.path.join('SampleOutputs', 'docs', 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{tool_name}.pdf")
    if DOCX2PDF_AVAILABLE:
        try:
            docx2pdf_convert(docx_path, pdf_path)
            print(f"Exported PDF to {pdf_path}")
        except Exception as e:
            print(f"PDF export failed for {tool_name}: {e}")
    else:
        print("docx2pdf not installed. Skipping PDF export.")
    # Check for missing key fields
    key_fields = KEY_FIELDS_SOFTWARE if tool_type == "software" else KEY_FIELDS_HARDWARE
    missing = [field for field in key_fields if info.get(field, "N/A") in ["N/A", "", None]]
    if missing:
        manual_review.append((tool_name_input, missing))

print("\nBatch processing complete.")
if manual_review:
    print("\nTools needing manual review (missing key fields):")
    for tool, fields in manual_review:
        print(f"- {tool}: missing {', '.join(fields)}")
else:
    print("All tools have key fields filled.")

# Only process Creative and Media Tools for now
# if __name__ == "__main__":
#     process_creative_media_tools()
#     # The other groups (AI/ML, Data Science, etc.) are complete and intentionally not processed here to avoid interference. 