from __future__ import annotations

import json

from ..models import Fix, Report

_LOCATION_LABELS = {
    "head": "Add to <head>",
    "body": "Add to <body>",
    "server": "Server-side actions",
    "content": "Content improvements",
}

_LOCATION_ORDER = ("head", "body", "server", "content")


def render_fixes_markdown(report: Report, fixes: list[Fix]) -> str:
    lines: list[str] = [f"# Pythia Fix — {report.url}", ""]

    if not fixes:
        lines += [f"✅ No fixes needed — score {report.score:.0f}/100", ""]
        return "\n".join(lines)

    lines += [f"Score: {report.score:.0f}/100 — **{len(fixes)} fix(es) needed**", ""]

    for location in _LOCATION_ORDER:
        group = [f for f in fixes if f.location == location]
        if not group:
            continue
        lines += [f"## {_LOCATION_LABELS[location]}", ""]
        for fix in group:
            icon = "❌" if fix.status == "FAIL" else "⚠️"
            lines += [f"### {icon} `{fix.check_name}`", ""]
            lines += ["```html", fix.snippet, "```"]
            if fix.note:
                lines.append(f"> {fix.note}")
            lines.append("")

    return "\n".join(lines)


def render_fixes_json(report: Report, fixes: list[Fix]) -> str:
    data = {
        "url": report.url,
        "score": report.score,
        "fixes_count": len(fixes),
        "fixes": [f.model_dump() for f in fixes],
    }
    return json.dumps(data, indent=2)
