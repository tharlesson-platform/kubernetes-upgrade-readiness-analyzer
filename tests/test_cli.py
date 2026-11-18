import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app


def test_scan_detects_blockers(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "scan",
            "--manifests-path",
            "fixtures/problematic",
            "--output-dir",
            str(tmp_path / "artifacts"),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "artifacts" / "report.json").exists()
    assert (tmp_path / "artifacts" / "report.html").exists()


def test_scan_ready_writes_consistent_reports(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "ready-report"
    result = CliRunner().invoke(
        app,
        ["scan", "--manifests-path", "fixtures/ready", "--target-version", "1.30",
         "--output-dir", str(output)],
    )
    assert result.exit_code == 0, result.stdout
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["readiness_score"] == 100
    assert report["blockers"] == []
    assert report["warnings"] == []
    assert report["target_version"] == "1.30"
    assert "readiness_score=100 blockers=0" in result.stdout
    for name in ("report.md", "report.html"):
        assert (output / name).stat().st_size > 0


def test_scan_missing_input_rejects_without_report(tmp_path: Path) -> None:
    output = tmp_path / "must-not-exist"
    result = CliRunner().invoke(
        app,
        ["scan", "--manifests-path", str(tmp_path / "missing"),
         "--output-dir", str(output)],
    )
    assert result.exit_code != 0
    assert not output.exists()


def test_gate_writes_reports_before_failing(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        ["scan", "--manifests-path", "fixtures/api-removal", "--source-version", "1.31",
         "--target-version", "1.32", "--output-dir", str(tmp_path), "--fail-on-blockers"],
    )
    assert result.exit_code == 1
    assert "upgrade_state=blocked" in result.stdout
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["source_version"] == "1.31"
    assert (tmp_path / "report.md").stat().st_size > 0
    assert (tmp_path / "report.html").stat().st_size > 0


def test_gate_does_not_approve_empty_scan(tmp_path: Path) -> None:
    manifests = tmp_path / "inputs"
    manifests.mkdir()
    (manifests / "values.yaml").write_text("replicaCount: 2\n", encoding="utf-8")
    output = tmp_path / "out"
    result = CliRunner().invoke(
        app, ["scan", "--manifests-path", str(manifests), "--output-dir", str(output), "--fail-on-blockers"],
    )
    assert result.exit_code == 2
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["upgrade_state"] == "indeterminate"
    assert report["coverage"]["manifest_count"] == 0


@pytest.mark.parametrize("versions", [("--target-version", "latest"), ("--source-version", "1.32", "--target-version", "1.31")])
def test_invalid_version_inputs_fail_before_writing_reports(tmp_path: Path, versions: tuple[str, ...]) -> None:
    output = tmp_path / "out"
    result = CliRunner().invoke(
        app, ["scan", "--manifests-path", "fixtures/ready", "--output-dir", str(output), *versions],
    )
    assert result.exit_code == 2
    assert not output.exists()
