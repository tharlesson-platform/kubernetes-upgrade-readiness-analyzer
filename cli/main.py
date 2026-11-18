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
    manifests_path: Path = typer.Option(..., exists=True, file_okay=False),
    target_version: str = typer.Option("1.29", help="Versão de destino, por exemplo 1.32."),
    source_version: str | None = typer.Option(None, help="Versão atual para classificar o impacto das remoções."),
    output_dir: Path = typer.Option(Path("artifacts")),
    fail_on_blockers: bool = typer.Option(False, "--fail-on-blockers", help="Retorna 1 com bloqueios ou 2 com evidência inconclusiva."),
) -> None:
    try:
        report = evaluate_manifest_directory(manifests_path, target_version, source_version)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (output_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
        (output_dir / "report.html").write_text(render_html(report), encoding="utf-8")
    except (OSError, ValueError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(2) from None
    score = report["readiness_score"] if report["readiness_score"] is not None else "n/a"
    console.print(f"readiness_score={score} blockers={len(report['blockers'])} upgrade_state={report['upgrade_state']}")
    if fail_on_blockers and report["blockers"]:
        raise typer.Exit(1)
    if fail_on_blockers and report["upgrade_state"] == "indeterminate":
        raise typer.Exit(2)
