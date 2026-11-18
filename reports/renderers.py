from __future__ import annotations

from html import escape


def _coverage_summary(report: dict) -> str:
    coverage = report["coverage"]
    addons_target = coverage["eks_addons_target_version"]
    addons = coverage["eks_addons"] if addons_target is None else f"{coverage['eks_addons']} ({addons_target})"
    return f"{coverage['manifest_count']} manifests, addons EKS: {addons}"


def render_markdown(report: dict) -> str:
    score = report["readiness_score"] if report["readiness_score"] is not None else "n/a"
    lines = [
        "# Kubernetes Upgrade Readiness Analyzer",
        "",
        f"- source_version: `{report['source_version'] or 'n/a'}`",
        f"- target_version: `{report['target_version']}`",
        f"- coverage: `{_coverage_summary(report)}`",
        f"- readiness_score: `{score}`",
        f"- upgrade_state: `{report['upgrade_state']}`",
        f"- summary_by_severity: `{report['summary_by_severity']}`",
        f"- summary_by_kind: `{report['summary_by_kind']}`",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- {item['resource']} -> {item['reason']}" for item in report["blockers"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {item['resource']} -> {item['reason']}" for item in report["warnings"])
    lines.extend(["", "## Checklist", ""])
    lines.extend(f"- {item}" for item in report["checklist"])
    return "\n".join(lines).strip() + "\n"


def render_html(report: dict) -> str:
    score = report["readiness_score"] if report["readiness_score"] is not None else "n/a"
    findings = "".join(
        f"<tr><td>{escape(item['severity'])}</td><td>{escape(item.get('category', 'general'))}</td><td>{escape(str(item.get('resource') or 'n/a'))}</td><td>{escape(item['reason'])}</td></tr>"
        for item in report["findings"]
    )
    return f"""<!doctype html>
<html lang='pt-BR'>
  <head>
    <meta charset='utf-8'>
    <title>Kubernetes Upgrade Readiness Analyzer</title>
    <style>
      body {{
        font-family: "Segoe UI", sans-serif;
        margin: 2rem auto;
        max-width: 1100px;
        padding: 0 1rem 3rem;
        background: #f8fafc;
        color: #0f172a;
      }}
      .hero {{
        background: linear-gradient(135deg, #dbeafe, #dcfce7);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1rem;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
      }}
      th, td {{
        padding: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
      }}
      th {{
        background: #e0f2fe;
      }}
    </style>
  </head>
  <body>
    <section class='hero'>
      <h1>Kubernetes Upgrade Readiness Analyzer</h1>
      <p><strong>source_version:</strong> {escape(report['source_version'] or 'n/a')} | <strong>target_version:</strong> {escape(report['target_version'])}</p>
      <p><strong>coverage:</strong> {escape(_coverage_summary(report))}</p>
      <p><strong>readiness_score:</strong> {score} | <strong>upgrade_state:</strong> {escape(report['upgrade_state'])}</p>
      <p><strong>summary_by_severity:</strong> {escape(str(report['summary_by_severity']))}</p>
    </section>
    <table>
      <thead>
        <tr>
          <th>Severity</th>
          <th>Category</th>
          <th>Resource</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>{findings}</tbody>
    </table>
  </body>
</html>"""
