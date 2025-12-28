import os
import json


_MAPPING_PATH = "mapping"


with open(os.path.join(_MAPPING_PATH, "mapping.json"), "r", encoding="utf-8") as f:
    _MAPPING: dict[str, str] = dict(json.load(f))


def get_category(note: str) -> str:
    return _MAPPING.get(note, f"Nezařazeno ('{note}')")
