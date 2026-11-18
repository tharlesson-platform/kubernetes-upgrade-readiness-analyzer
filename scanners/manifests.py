from __future__ import annotations

from pathlib import Path

import yaml


def _resources(item: object, path: Path) -> list[dict]:
    if not isinstance(item, dict) or not ("apiVersion" in item or "kind" in item):
        return []
    if item.get("apiVersion") == "v1" and item.get("kind") == "List":
        items = item.get("items")
        if not isinstance(items, list) or any(
            not isinstance(resource, dict) or resource.get("kind") in (None, "List") for resource in items
        ):
            raise ValueError(f"List de recursos inválida em {path}.")
        return [resource for entry in items for resource in _resources(entry, path)]
    if any(not isinstance(item.get(key), str) or not item[key] for key in ("apiVersion", "kind")):
        raise ValueError(f"Recurso sem apiVersion ou kind válido em {path}.")
    if item["kind"] == "Kustomization" and item["apiVersion"].startswith("kustomize.config.k8s.io/"):
        return []
    for key in ("metadata", "spec"):
        if item.get(key) is not None and not isinstance(item[key], dict):
            raise ValueError(f"Campo {key} inválido em {path}.")
    return [{**item, "_source": str(path)}]


def load_documents(directory: Path) -> list[dict]:
    documents: list[dict] = []
    for path in sorted(directory.rglob("*")):
        if path.suffix.lower() not in {".yaml", ".yml"} or not path.is_file():
            continue
        try:
            for item in yaml.safe_load_all(path.read_text(encoding="utf-8")):
                documents.extend(_resources(item, path))
        except (yaml.YAMLError, UnicodeError):
            raise ValueError(f"YAML inválido em {path}.") from None
    return documents
