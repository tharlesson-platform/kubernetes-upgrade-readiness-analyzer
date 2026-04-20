from pathlib import Path

from typer.testing import CliRunner

from cli.main import app


def test_scan_detects_blockers() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", "--manifests-path", "fixtures/problematic"])
    assert result.exit_code == 0, result.stdout
    assert Path("artifacts/report.json").exists()
