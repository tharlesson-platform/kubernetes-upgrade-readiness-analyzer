import json
from pathlib import Path

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
