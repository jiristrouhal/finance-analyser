import os
import json


_MAPPING_PATH = "mapping"


with open(os.path.join(_MAPPING_PATH, "mapping.json"), "r", encoding="utf-8") as f:
    _MAPPING: dict[str, dict[str, str]] = dict(json.load(f))
    orig_partial = dict(_MAPPING["partial"])
    for key in orig_partial:
        _MAPPING["partial"][key.lower()] = _MAPPING["partial"].pop(key)


def get_category(*keys: str) -> str:
    """Gets the category for a given key based on the mapping."""
    for key in keys:
        category = _MAPPING["exact"].get(key, "")
        if category:
            return category
        # There is no exact match, try partial matches
        for pattern in _MAPPING["partial"]:
            if pattern in key.lower():
                return _MAPPING["partial"][pattern]
    return f"Nezařazeno {keys}"
