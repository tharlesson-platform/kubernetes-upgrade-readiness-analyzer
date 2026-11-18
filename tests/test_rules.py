import json
from pathlib import Path

import pytest
import yaml

from rules.catalog import evaluate_manifest_directory
from rules.workloads import matching_pdbs


def test_evaluate_manifest_directory_reads_addons() -> None:
    report = evaluate_manifest_directory(Path("fixtures/problematic"), "1.29")
    assert any(item["resource"] == "aws-ebs-csi-driver" for item in report["blockers"])
    assert report["checklist"]
    assert report["upgrade_state"] == "blocked"
    assert report["summary_by_severity"]["blocker"] >= 1


def test_evaluate_manifest_directory_ready_fixture() -> None:
    report = evaluate_manifest_directory(Path("fixtures/ready"), "1.29")
    assert report["readiness_score"] == 100
    assert report["blockers"] == []
    assert report["warnings"] == []
    assert report["summary_by_kind"]["PodDisruptionBudget"] == 1


@pytest.mark.parametrize(
    ("source", "target", "impact"),
    [
        ("v1.30.2", "1.31", None),
        ("1.31", "v1.32.0", "removed_during_upgrade"),
        ("1.32", "1.33", "already_unavailable_at_source"),
        (None, "1.32", "unavailable_at_target"),
    ],
)
def test_flowschema_removal_depends_on_target_and_source(source, target, impact) -> None:
    report = evaluate_manifest_directory(Path("fixtures/api-removal"), target, source)
    if impact is None:
        assert report["blockers"] == []
    else:
        [finding] = report["blockers"]
        assert finding["removed_in"] == "1.32"
        assert finding["impact"] == impact
        assert finding["api_version"] == "flowcontrol.apiserver.k8s.io/v1beta3"


@pytest.mark.parametrize(("minor", "expected"), [(24, []), (25, ["early"]), (26, ["early", "late"])])
def test_hpa_beta_apis_have_different_removal_releases(tmp_path: Path, minor: int, expected: list[str]) -> None:
    manifests = [
        {"apiVersion": f"autoscaling/v2beta{version}", "kind": "HorizontalPodAutoscaler", "metadata": {"name": name}}
        for version, name in ((1, "early"), (2, "late"))
    ]
    manifest_list = {"apiVersion": "v1", "kind": "List", "items": manifests}
    (tmp_path / "hpa.yaml").write_text(yaml.safe_dump(manifest_list), encoding="utf-8")
    report = evaluate_manifest_directory(tmp_path, f"1.{minor}")
    assert [item["resource"] for item in report["blockers"]] == expected
    assert report["coverage"]["manifest_count"] == 2


def _deployment() -> dict:
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "api",
            "namespace": "payments",
            "labels": {"pod-security.kubernetes.io/enforce": "baseline", "tier": "other"},
        },
        "spec": {"replicas": 2, "template": {"metadata": {"labels": {"app": "api", "tier": "web", "track": "stable"}}}},
    }


def _budget(selector: dict | None, api_version: str = "policy/v1") -> dict:
    return {
        "apiVersion": api_version,
        "kind": "PodDisruptionBudget",
        "metadata": {"name": "api", "namespace": "payments"},
        "spec": {"minAvailable": 1, "selector": selector},
    }


@pytest.mark.parametrize(
    ("selector", "api_version", "minor", "expected"),
    [
        ({}, "policy/v1", 32, 1),
        (None, "policy/v1", 32, 0),
        ({"matchLabels": []}, "policy/v1", 32, 0),
        ({}, "policy/v1beta1", 24, 0),
        ({"matchLabels": {"app": "api"}}, "policy/v1beta1", 25, 0),
        ({"matchLabels": {"app": "api", "tier": "web"}}, "policy/v1", 32, 1),
        ({"matchLabels": {"app": "api", "tier": "other"}}, "policy/v1", 32, 0),
        (
            {"matchExpressions": [
                {"key": "track", "operator": "In", "values": ["stable"]},
                {"key": "unrelated", "operator": "NotIn", "values": ["canary"]},
                {"key": "app", "operator": "Exists"},
                {"key": "debug", "operator": "DoesNotExist"},
            ]},
            "policy/v1",
            32,
            1,
        ),
        ({"matchExpressions": [{"key": "track", "operator": "In", "values": ["canary"]}]}, "policy/v1", 32, 0),
    ],
)
def test_pdbs_match_pod_template_and_target(selector, api_version, minor, expected) -> None:
    assert matching_pdbs(_deployment(), [_budget(selector, api_version)], minor) == expected


def test_namespace_policy_and_pdb_are_scoped_to_the_deployment_namespace(tmp_path: Path) -> None:
    deployment = _deployment()
    namespace = {
        "apiVersion": "v1", "kind": "Namespace",
        "metadata": {"name": "other", "labels": {"pod-security.kubernetes.io/enforce": "restricted"}},
    }
    budget = _budget({"matchLabels": {"app": "api"}})
    budget["metadata"]["namespace"] = "other"
    (tmp_path / "workload.yaml").write_text(yaml.safe_dump_all([deployment, namespace, budget]), encoding="utf-8")
    report = evaluate_manifest_directory(tmp_path, "1.32")
    assert {item["category"] for item in report["warnings"]} == {"pod-security", "availability"}


def test_versioned_addons_only_apply_to_their_target(tmp_path: Path) -> None:
    source = Path("fixtures/api-removal/flowschema.yaml")
    (tmp_path / "flowschema.yaml").write_bytes(source.read_bytes())
    snapshot = {"target_version": "v1.30.1", "addons": [{"name": "coredns", "status": "unsupported"}]}
    (tmp_path / "eks-addons.json").write_text(json.dumps(snapshot), encoding="utf-8")
    matched = evaluate_manifest_directory(tmp_path, "1.30")
    assert matched["coverage"]["eks_addons"] == "matched"
    assert matched["upgrade_state"] == "blocked"
    mismatch = evaluate_manifest_directory(tmp_path, "1.31")
    assert mismatch["coverage"]["eks_addons"] == "target_mismatch"
    assert mismatch["upgrade_state"] == "indeterminate"
    assert mismatch["readiness_score"] is None
    assert mismatch["blockers"] == []


def test_kustomization_config_alone_does_not_count_as_rendered_manifests(tmp_path: Path) -> None:
    config = tmp_path / "kustomization.yaml"
    config.write_text("kind: Kustomization\napiVersion: kustomize.config.k8s.io/v1beta1\n", encoding="utf-8")
    report = evaluate_manifest_directory(tmp_path, "1.32")
    assert report["coverage"]["manifest_count"] == 0
    assert report["upgrade_state"] == "indeterminate"
