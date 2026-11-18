from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from rules import addons as addon_rules
from rules.api_versions import REMOVED_APIS, version_minor
from rules.workloads import matching_pdbs, namespace, namespace_enforces_pod_security
from scanners.addons import load_addons
from scanners.manifests import load_documents


def _finding(item: dict, severity: str, category: str, reason: str) -> dict:
    return {
        "resource": (item.get("metadata") or {}).get("name"),
        "reason": reason,
        "source": item["_source"],
        "severity": severity,
        "category": category,
    }


def _api_removal(item: dict, source_minor: int | None, target_minor: int) -> dict | None:
    api_version, kind = item["apiVersion"], item["kind"]
    removal = REMOVED_APIS.get((api_version, kind))
    if removal is None or target_minor < removal[0]:
        return None
    removed_minor, migration = removal
    removed_in = f"1.{removed_minor}"
    if source_minor is None:
        impact = "unavailable_at_target"
    elif source_minor >= removed_minor:
        impact = "already_unavailable_at_source"
    else:
        impact = "removed_during_upgrade"
    return {
        **_finding(item, "blocker", "api-deprecation", f"{kind} em {api_version} removida no Kubernetes {removed_in}. {migration}."),
        "api_version": api_version,
        "removed_in": removed_in,
        "impact": impact,
    }


def evaluate_manifest_directory(directory: Path, target_version: str, source_version: str | None = None) -> dict:
    target_minor = version_minor(target_version)
    source_minor = version_minor(source_version) if source_version is not None else None
    if source_minor is not None and source_minor > target_minor:
        raise ValueError("A versão de origem é posterior à versão-alvo.")
    blockers = []
    warnings = []
    docs = load_documents(directory)
    kind_summary = Counter(item["kind"] for item in docs)
    budgets = defaultdict(list)
    protected_namespaces = set()
    for item in docs:
        if item["kind"] == "PodDisruptionBudget" and item["apiVersion"] in ("policy/v1", "policy/v1beta1"):
            budgets[namespace(item)].append(item)
        if item["kind"] == "Namespace" and item["apiVersion"] == "v1" and namespace_enforces_pod_security(item):
            protected_namespaces.add(item["metadata"].get("name"))
    for item in docs:
        removal = _api_removal(item, source_minor, target_minor)
        if removal:
            blockers.append(removal)
        kind, api_version, spec = item["kind"], item["apiVersion"], item.get("spec") or {}
        if (api_version, kind) == ("networking.k8s.io/v1", "Ingress") and not spec.get("ingressClassName"):
            warnings.append(_finding(item, "warning", "ingress", "Ingress sem ingressClassName"))
        if (api_version, kind) == ("apiextensions.k8s.io/v1", "CustomResourceDefinition") and not spec.get("versions"):
            warnings.append(_finding(item, "warning", "crd", "CRD sem versions declaradas"))
        if (api_version, kind) == ("apps/v1", "Deployment"):
            if target_minor >= 23 and namespace(item) not in protected_namespaces:
                warnings.append(_finding(item, "warning", "pod-security", "Namespace sem política enforce baseline/restricted nos manifests"))
            replicas = spec.get("replicas")
            if replicas is not None and (type(replicas) is not int or replicas < 0):
                raise ValueError(f"Número de réplicas inválido em {item['_source']}.")
            if replicas is not None and replicas > 1:
                count = matching_pdbs(item, budgets[namespace(item)], target_minor)
                if count == 0:
                    warnings.append(_finding(item, "warning", "availability", "Nenhum PDB válido para o alvo seleciona os Pods do Deployment"))
                elif count > 1:
                    warnings.append(_finding(item, "warning", "availability", "Mais de um PDB seleciona os mesmos Pods do Deployment"))

    addons, addons_target = load_addons(directory)
    if addons is None:
        addon_coverage = "missing"
    elif addons_target is None:
        addon_coverage = "unversioned"
    elif version_minor(addons_target) == target_minor:
        addon_coverage = "matched"
    else:
        addon_coverage = "target_mismatch"
        addons = None
    addon_blockers, addon_warnings = addon_rules.evaluate(addons or [])
    blockers.extend(addon_blockers)
    warnings.extend(addon_warnings)
    incomplete = not docs or addon_coverage == "target_mismatch"
    if blockers:
        upgrade_state = "blocked"
    elif incomplete:
        upgrade_state = "indeterminate"
    else:
        upgrade_state = "attention" if warnings else "ready"
    return {
        "title": "Kubernetes Upgrade Readiness Analyzer",
        "source_version": source_version,
        "target_version": target_version,
        "readiness_score": None if incomplete else max(0, 100 - (len(blockers) * 25) - (len(warnings) * 5)),
        "upgrade_state": upgrade_state,
        "coverage": {
            "manifest_count": len(docs),
            "eks_addons": addon_coverage,
            "eks_addons_target_version": addons_target,
        },
        "summary_by_severity": {"blocker": len(blockers), "warning": len(warnings)},
        "summary_by_kind": kind_summary,
        "findings": blockers + warnings,
        "blockers": blockers,
        "warnings": warnings,
        "checklist": [
            "Remover APIs deprecated",
            "Validar addons EKS e CRDs",
            "Confirmar PDBs e HPA compativeis com a versao alvo",
            "Reexecutar scan após renderização Helm final",
        ],
    }
