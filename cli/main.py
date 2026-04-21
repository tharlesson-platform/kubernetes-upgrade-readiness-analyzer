from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from reports.renderers import render_html, render_markdown
from rules.catalog import evaluate_manifest_directory


app = typer.Typer(help="Assess Kubernetes/EKS upgrade readiness from local manifests.")
console = Console()


def run() -> None:
    app()


@app.command()
def version() -> None:
    console.print("0.1.0")


@app.command()
def scan(
    manifests_path: Path = typer.Option(..., exists=True),
    target_version: str = typer.Option("1.29"),
    output_dir: Path = typer.Option(Path("artifacts")),
) -> None:
    report = evaluate_manifest_directory(manifests_path, target_version)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
    (output_dir / "report.html").write_text(render_html(report), encoding="utf-8")
    console.print(f"readiness_score={report['readiness_score']} blockers={len(report['blockers'])}")
