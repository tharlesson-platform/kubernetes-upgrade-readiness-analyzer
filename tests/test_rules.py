from pathlib import Path

from rules.catalog import evaluate_manifest_directory


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
