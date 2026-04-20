from pathlib import Path

from rules.catalog import evaluate_manifest_directory


def test_evaluate_manifest_directory_reads_addons() -> None:
    report = evaluate_manifest_directory(Path("fixtures/problematic"), "1.29")
    assert any(item["resource"] == "aws-ebs-csi-driver" for item in report["blockers"])
    assert report["checklist"]
