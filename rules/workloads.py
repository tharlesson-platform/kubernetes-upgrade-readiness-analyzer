"""Check namespace policies and Pod Disruption Budgets for Deployments."""

from __future__ import annotations

from rules.api_versions import REMOVED_APIS


def namespace(item: dict) -> str:
    return (item.get("metadata") or {}).get("namespace") or "default"


def namespace_enforces_pod_security(item: dict) -> bool:
    labels = (item.get("metadata") or {}).get("labels")
    return isinstance(labels, dict) and labels.get("pod-security.kubernetes.io/enforce") in ("baseline", "restricted")


def _matches_expression(expression: dict, pod_labels: dict) -> bool:
    key = expression.get("key")
    operator = expression.get("operator")
    values = expression.get("values")
    if values is None:
        values = []
    if not isinstance(key, str) or not isinstance(values, list):
        return False
    if operator == "In":
        return bool(values) and key in pod_labels and pod_labels[key] in values
    if operator == "NotIn":
        return bool(values) and (key not in pod_labels or pod_labels[key] not in values)
    if operator == "Exists":
        return not values and key in pod_labels
    if operator == "DoesNotExist":
        return not values and key not in pod_labels
    return False


def _matches_selector(selector: dict, pod_labels: dict) -> bool:
    if set(selector) - {"matchLabels", "matchExpressions"}:
        return False
    labels = selector.get("matchLabels")
    expressions = selector.get("matchExpressions")
    if labels is None:
        labels = {}
    if expressions is None:
        expressions = []
    return (
        isinstance(labels, dict)
        and isinstance(expressions, list)
        and all(key in pod_labels and pod_labels[key] == value for key, value in labels.items())
        and all(isinstance(expression, dict) and _matches_expression(expression, pod_labels) for expression in expressions)
    )


def matching_pdbs(deployment: dict, budgets: list[dict], target_minor: int) -> int:
    template = deployment["spec"].get("template")
    metadata = template.get("metadata") if isinstance(template, dict) else None
    pod_labels = metadata.get("labels") if isinstance(metadata, dict) else {}
    if pod_labels is None:
        pod_labels = {}
    if not isinstance(pod_labels, dict):
        raise ValueError(f"Labels do template de Pods inválidas em {deployment['_source']}.")
    matches = 0
    for budget in budgets:
        api_version = budget["apiVersion"]
        removal = REMOVED_APIS.get((api_version, "PodDisruptionBudget"))
        if removal and target_minor >= removal[0]:
            continue
        if api_version == "policy/v1" and target_minor < 21:
            continue
        selector = (budget.get("spec") or {}).get("selector")
        if not isinstance(selector, dict):
            continue
        if api_version == "policy/v1beta1" and not (selector.get("matchLabels") or selector.get("matchExpressions")):
            continue
        if _matches_selector(selector, pod_labels):
            matches += 1
    return matches
