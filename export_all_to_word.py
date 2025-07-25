import os
import sys
import glob
from export_to_word import export_metadata_to_word

def find_json_files(directory):
    return glob.glob(os.path.join(directory, '*.json'))

def main():
    # Default directories
    default_dirs = [
        os.path.join('SampleOutputs', 'metadata', 'Non-PyPI'),
        os.path.join('SampleOutputs', 'metadata', 'PyPI')
    ]
    # Use user-supplied directory if given
    if len(sys.argv) > 1:
        dirs = [sys.argv[1]]
    else:
        dirs = default_dirs
    all_jsons = []
    for d in dirs:
        if os.path.isdir(d):
            all_jsons.extend(find_json_files(d))
    if not all_jsons:
        print('No JSON files found in the specified directories.')
        return
    print(f'Found {len(all_jsons)} JSON files. Converting...')
    # When saving DOCX files, use 'SampleOutputs/docs/docx/'
    docx_dir = os.path.join('SampleOutputs', 'docs', 'docx')
    os.makedirs(docx_dir, exist_ok=True)
    # When saving PDF files, use 'SampleOutputs/docs/pdf/'
    pdf_dir = os.path.join('SampleOutputs', 'docs', 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    for json_file in all_jsons:
        print(f'Converting: {json_file}')
        try:
            # Load metadata
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = f.read()
            import json as _json
            metadata = _json.loads(metadata)
            tool_name = metadata.get('General Information', {}).get('Name') or metadata.get('Name', 'output')
            output_path = os.path.join(docx_dir, f"{tool_name}.docx")
            export_metadata_to_word(metadata, output_path)
        except Exception as e:
            print(f'Failed to convert {json_file}: {e}')
    print('Batch conversion complete.')

if __name__ == '__main__':
    main() 