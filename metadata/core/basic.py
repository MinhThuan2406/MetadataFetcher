"""
Simple output processor for UnifiedMetadata.
Exports metadata to JSON and YAML formats.
"""

import json
import yaml
from typing import Union
from .schema import UnifiedMetadata


def save_to_json(metadata: Union[UnifiedMetadata, dict], file_path: str, ensure_ascii: bool = False) -> None:
    """
    Save UnifiedMetadata (or dict) to a JSON file.
    """
    if isinstance(metadata, UnifiedMetadata):
        data = metadata.to_dict()
    else:
        data = metadata
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)


def save_to_yaml(metadata: Union[UnifiedMetadata, dict], file_path: str) -> None:
    """
    Save UnifiedMetadata (or dict) to a YAML file.
    """
    if isinstance(metadata, UnifiedMetadata):
        data = metadata.to_dict()
    else:
        data = metadata
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True) 