from __future__ import annotations

from ..models import Report

STATUS_ICONS = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌", "SKIP": "⏭️ "}
CATEGORY_WEIGHTS = {"structure": 40, "html": 30, "content": 30}


def _score_bar(score: float, width: int = 10) -> str:
    filled = round(score / 100 * width)
    return "●" * filled + "○" * (width - filled)


def render_markdown(report: Report) -> str:
    lines: list[str] = []

    status_str = "✅ PASS" if report.passed else "❌ FAIL"
    lines += [
        f"# Pythia GEO Audit — {report.url}",
        "",
        f"**Score: {report.score:.0f}/100**  {_score_bar(report.score)}  "
        f"{status_str} *(threshold: {report.threshold})*",
        "",
    ]

    for category in ["structure", "html", "content"]:
        cat_results = [r for r in report.results if r.category == category]
        if not cat_results:
            continue
        cat_score = report.scores_by_category.get(category, 0.0)
        weight = CATEGORY_WEIGHTS[category]
        lines += [
            f"## {category.upper()} ({weight}%)  —  {cat_score:.0f}/100",
            "",
        ]
        for r in cat_results:
            icon = STATUS_ICONS.get(r.status, "?")
            lines.append(f"- {icon} **{r.status}** `{r.name}` — {r.message}")
        lines.append("")

    recs = [(r.name, r.recommendation) for r in report.results if r.recommendation]
    if recs:
        lines += ["## Recommendations", ""]
        for name, rec in recs:
            lines.append(f"- **`{name}`** — {rec}")
        lines.append("")

    return "\n".join(lines)
