from __future__ import annotations


def evaluate(addons: list[dict]) -> tuple[list[dict], list[dict]]:
    blockers = []
    warnings = []
    for addon in addons:
        if addon.get("status") == "unsupported":
            blockers.append({"resource": addon["name"], "reason": "Addon sem suporte para a versao alvo", "source": "eks-addons.json", "severity": "blocker", "category": "eks-addon"})
        elif addon.get("status") == "upgrade-required":
            warnings.append({"resource": addon["name"], "reason": "Addon exige upgrade antes do cluster", "source": "eks-addons.json", "severity": "warning", "category": "eks-addon"})
    return blockers, warnings
