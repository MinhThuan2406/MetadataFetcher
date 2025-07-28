#!/usr/bin/env python3
"""
Script to convert ollama.json in PrototypeOutputs to TXT format.
Writes the result into the top‑level 'txt' folder next to the JSON folders.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict


def format_value(value: Any, indent: int = 0) -> str:
    indent_str = "  " * indent
    if isinstance(value, dict):
        lines = []
        for key, val in value.items():
            if isinstance(val, (list, dict)):
                lines.append(f"{indent_str}{key}:")
                lines.append(format_value(val, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {val}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (list, dict)):
                lines.append(format_value(item, indent))
            else:
                lines.append(f"{indent_str}- {item}")
        return "\n".join(lines)
    return f"{indent_str}{value}"


def convert_json_to_txt(json_content: Dict[str, Any]) -> str:
    lines = []
    tool_name = json_content.get("tool_name", "Unknown Tool")
    lines.append("TOOL METADATA REPORT")
    lines.append(f"Tool Name: {tool_name}")
    lines.append("")
    for key, value in json_content.items():
        if key == "tool_name":
            continue
        section = key.replace("_", " ").title()
        lines.append(section)
        lines.append("-" * len(section))
        if isinstance(value, (list, dict)):
            lines.append(format_value(value, 1))
        else:
            lines.append(f"  {value}")
        lines.append("")
    return "\n".join(lines)


def convert_file(json_path: Path, output_dir: Path) -> bool:
    try:
        content = json.loads(json_path.read_text(encoding="utf-8"))
        txt = convert_json_to_txt(content)
        txt_path = output_dir / f"{json_path.stem}.txt"
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        txt_path.write_text(txt, encoding="utf-8")
        print(f"✓ Converted: {json_path.name} -> {txt_path.name}")
        return True
    except Exception as e:
        print(f"✗ Error converting {json_path.name}: {e}")
        return False


# def main():
#     script_dir = Path(__file__).parent
#     project_root = script_dir.parent

#     json_file = project_root / "PrototypeOutputs/llm_tools/json/ollama.json"
#     output_dir = project_root / "PrototypeOutputs/txt"

#     if not json_file.exists():
#         print(f"Error: JSON file not found at {json_file}")
#         sys.exit(1)

#     output_dir.mkdir(parents=True, exist_ok=True)
#     print(f"Writing to existing folder: {output_dir}\n")

#     success = convert_file(json_file, output_dir)

#     print("CONVERSION SUMMARY")
#     print(f"Total files processed: 1")
#     print(f"Successful conversions: {1 if success else 0}")
#     print(f"Failed conversions: {0 if success else 1}")
#     if success:
#         print(f"\nTXT file saved as: {output_dir / (json_file.stem + '.txt')}")



# Convert all JSON files at once
def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    input_root = project_root / "PrototypeOutputs"
    output_dir = input_root / "txt"

    if not input_root.exists():
        print(f"Error: Directory not found: {input_root}")
        sys.exit(1)

    json_files = list(input_root.rglob("*.json"))
    if not json_files:
        print("No JSON files found.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(json_files)} JSON files")
    print(f"Writing converted TXT files to: {output_dir}\n")

    success_count = 0
    fail_count = 0

    for json_file in json_files:
        if convert_file(json_file, output_dir):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {len(json_files)}")
    print(f"Successful conversions: {success_count}")
    print(f"Failed conversions: {fail_count}")
    print(f"TXT files saved to: {output_dir}")



if __name__ == "__main__":
    main()
