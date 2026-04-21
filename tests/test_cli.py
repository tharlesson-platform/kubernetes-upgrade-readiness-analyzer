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
