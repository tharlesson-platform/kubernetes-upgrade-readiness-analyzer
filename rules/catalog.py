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


def _blocker(resource: str | None, reason: str, source: str, category: str) -> dict:
    return {"resource": resource, "reason": reason, "source": source, "severity": "blocker", "category": category}


def _warning(resource: str | None, reason: str, source: str, category: str) -> dict:
    return {"resource": resource, "reason": reason, "source": source, "severity": "warning", "category": category}


def _deployment_identity(item: dict) -> tuple[str | None, str | None]:
    metadata = item.get("metadata", {})
    labels = metadata.get("labels", {})
    return metadata.get("namespace", "default"), labels.get("app") or metadata.get("name")


def evaluate_manifest_directory(directory, target_version: str) -> dict:
    blockers = []
    warnings = []
    docs = load_documents(directory)
    kind_summary: dict[str, int] = {}
    pdb_targets: set[tuple[str | None, str | None]] = set()
    for item in docs:
        kind = item.get("kind", "Unknown")
        kind_summary[kind] = kind_summary.get(kind, 0) + 1
        if item.get("kind") == "PodDisruptionBudget":
            metadata = item.get("metadata", {})
            selector = item.get("spec", {}).get("selector", {}).get("matchLabels", {})
            pdb_targets.add((metadata.get("namespace", "default"), selector.get("app") or metadata.get("name")))
    for item in docs:
        key = (item.get("apiVersion"), item.get("kind"))
        if key in DEPRECATED:
            blockers.append(_blocker(item.get("metadata", {}).get("name"), DEPRECATED[key], item["_source"], "api-deprecation"))
        if item.get("apiVersion") == "networking.k8s.io/v1" and item.get("kind") == "Ingress":
            if not item.get("spec", {}).get("ingressClassName"):
                warnings.append(_warning(item.get("metadata", {}).get("name"), "Ingress sem ingressClassName", item["_source"], "ingress"))
        if item.get("kind") == "Deployment" and "pod-security.kubernetes.io/enforce" not in item.get("metadata", {}).get("labels", {}):
            warnings.append(_warning(item.get("metadata", {}).get("name"), "Label de Pod Security nao encontrada", item["_source"], "pod-security"))
        if item.get("kind") == "Deployment" and int(item.get("spec", {}).get("replicas", 1)) > 1:
            if _deployment_identity(item) not in pdb_targets:
                warnings.append(_warning(item.get("metadata", {}).get("name"), "Deployment com replicas > 1 sem PodDisruptionBudget associado", item["_source"], "availability"))
        if item.get("kind") == "HorizontalPodAutoscaler" and item.get("apiVersion") in {"autoscaling/v2beta1", "autoscaling/v2beta2"}:
            blockers.append(_blocker(item.get("metadata", {}).get("name"), "Migrar HPA para autoscaling/v2 antes do upgrade", item["_source"], "api-deprecation"))
        if item.get("kind") == "CustomResourceDefinition" and item.get("apiVersion") == "apiextensions.k8s.io/v1":
            versions = item.get("spec", {}).get("versions", [])
            if not versions:
                warnings.append(_warning(item.get("metadata", {}).get("name"), "CRD sem versions declaradas", item["_source"], "crd"))
    addon_blockers, addon_warnings = addon_rules.evaluate(load_addons(directory))
    blockers.extend(addon_blockers)
    warnings.extend(addon_warnings)
    readiness_score = max(0, 100 - (len(blockers) * 25) - (len(warnings) * 5))
    findings = blockers + warnings
    upgrade_state = "blocked" if blockers else ("attention" if warnings else "ready")
    return {
        "title": "Kubernetes Upgrade Readiness Analyzer",
        "target_version": target_version,
        "readiness_score": readiness_score,
        "upgrade_state": upgrade_state,
        "summary_by_severity": {"blocker": len(blockers), "warning": len(warnings)},
        "summary_by_kind": kind_summary,
        "findings": findings,
        "blockers": blockers,
        "warnings": warnings,
        "checklist": [
            "Remover APIs deprecated",
            "Validar addons EKS e CRDs",
            "Confirmar PDBs e HPA compativeis com a versao alvo",
            "Reexecutar scan após renderização Helm final",
        ],
    }
