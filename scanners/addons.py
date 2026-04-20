from __future__ import annotations

import json
from pathlib import Path


def load_addons(directory: Path) -> list[dict]:
    addons_file = directory / "eks-addons.json"
    if not addons_file.exists():
        return []
    return json.loads(addons_file.read_text(encoding="utf-8"))
