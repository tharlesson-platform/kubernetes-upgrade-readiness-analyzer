from __future__ import annotations

from pathlib import Path

import yaml


def load_documents(directory: Path) -> list[dict]:
    documents = []
    for path in directory.rglob("*.y*ml"):
        for item in yaml.safe_load_all(path.read_text(encoding="utf-8")):
            if item:
                item["_source"] = str(path)
                documents.append(item)
    return documents
