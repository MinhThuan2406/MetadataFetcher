import os
import sys
import glob
from export_to_word import json_to_professional_word

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
    for json_file in all_jsons:
        print(f'Converting: {json_file}')
        try:
            json_to_professional_word(json_file)
        except Exception as e:
            print(f'Failed to convert {json_file}: {e}')
    print('Batch conversion complete.')

if __name__ == '__main__':
    main() 