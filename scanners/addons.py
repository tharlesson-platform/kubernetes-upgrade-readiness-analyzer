from __future__ import annotations

import json
from pathlib import Path


def load_addons(directory: Path) -> tuple[list[dict] | None, str | None]:
    addons_file = directory / "eks-addons.json"
    if not addons_file.exists():
        return None, None
    try:
        payload = json.loads(addons_file.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        raise ValueError("eks-addons.json inválido.") from None
    target = None
    if isinstance(payload, dict):
        target = payload.get("target_version")
        if not isinstance(target, str):
            raise ValueError("O snapshot versionado de addons requer target_version.")
        payload = payload.get("addons")
    if not isinstance(payload, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]
        or item.get("status") not in ("supported", "unsupported", "upgrade-required")
        for item in payload
    ):
        raise ValueError("Cada addon precisa de nome e status supported, unsupported ou upgrade-required.")
    return payload, target
