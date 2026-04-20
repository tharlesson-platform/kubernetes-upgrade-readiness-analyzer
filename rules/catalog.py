from __future__ import annotations

from rules import addons as addon_rules
from scanners.addons import load_addons
from scanners.manifests import load_documents


DEPRECATED = {
    ("extensions/v1beta1", "Ingress"): "Use networking.k8s.io/v1",
    ("networking.k8s.io/v1beta1", "Ingress"): "Use networking.k8s.io/v1",
    ("policy/v1beta1", "PodSecurityPolicy"): "PodSecurityPolicy foi removido; migrar para Pod Security Admission",
    ("apiextensions.k8s.io/v1beta1", "CustomResourceDefinition"): "Migrar CRD para apiextensions.k8s.io/v1",
}


def evaluate_manifest_directory(directory, target_version: str) -> dict:
    blockers = []
    warnings = []
    docs = load_documents(directory)
    for item in docs:
        key = (item.get("apiVersion"), item.get("kind"))
        if key in DEPRECATED:
            blockers.append({"resource": item.get("metadata", {}).get("name"), "reason": DEPRECATED[key], "source": item["_source"]})
        if item.get("apiVersion") == "networking.k8s.io/v1" and item.get("kind") == "Ingress":
            if not item.get("spec", {}).get("ingressClassName"):
                warnings.append({"resource": item.get("metadata", {}).get("name"), "reason": "Ingress sem ingressClassName", "source": item["_source"]})
        if item.get("kind") == "Deployment" and "pod-security.kubernetes.io/enforce" not in item.get("metadata", {}).get("labels", {}):
            warnings.append({"resource": item.get("metadata", {}).get("name"), "reason": "Label de Pod Security não encontrada", "source": item["_source"]})
        if item.get("kind") == "CustomResourceDefinition" and item.get("apiVersion") == "apiextensions.k8s.io/v1":
            versions = item.get("spec", {}).get("versions", [])
            if not versions:
                warnings.append({"resource": item.get("metadata", {}).get("name"), "reason": "CRD sem versions declaradas", "source": item["_source"]})
    addon_blockers, addon_warnings = addon_rules.evaluate(load_addons(directory))
    blockers.extend(addon_blockers)
    warnings.extend(addon_warnings)
    readiness_score = max(0, 100 - (len(blockers) * 25) - (len(warnings) * 5))
    return {
        "title": "Kubernetes Upgrade Readiness Analyzer",
        "target_version": target_version,
        "readiness_score": readiness_score,
        "blockers": blockers,
        "warnings": warnings,
        "checklist": [
            "Remover APIs deprecated",
            "Validar addons EKS e CRDs",
            "Reexecutar scan após renderização Helm final",
        ],
    }
