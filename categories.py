import os
import json

from constants import MAPPING_DIR as _MAPPING_DIR


mappings = [
    os.path.join(_MAPPING_DIR, filename)
    for filename in os.listdir(_MAPPING_DIR)
    if filename.endswith(".json")
]
MAPPING: dict[str, dict[str, str] | list[str]] = {}
for path in mappings:
    with open(path, "r", encoding="utf-8") as f:
        curr_mapping: dict[str, dict[str, str]] = dict(json.load(f))
        orig_partial = dict(curr_mapping["partial"])
        for key in orig_partial:
            curr_mapping["partial"][key.lower()] = curr_mapping["partial"].pop(key)
    for key in ["exact", "partial", "category_replace"]:
        if not key in MAPPING:
            MAPPING[key] = {}
        MAPPING[key].update(curr_mapping[key])
    if not "skip" in MAPPING:
        MAPPING["skip"] = []
    MAPPING["skip"].extend(curr_mapping["skip"])


def get_category(*keys: str) -> str:
    """Gets the category for a given key based on the mapping."""
    keys = tuple([key.strip() for key in keys if key.strip()])
    for key in keys:
        category = MAPPING["exact"].get(key, "")
        if category:
            return category
        # There is no exact match, try partial matches
        for pattern in MAPPING["partial"]:
            if pattern in key.lower():
                return MAPPING["partial"][pattern]
    return f"Nezařazeno {keys}"


def replace_category(old: str) -> str:
    """Replaces category in the transaction, if the replacement exists in the mapping."""
    return MAPPING["category_replace"].get(old, "") or old
