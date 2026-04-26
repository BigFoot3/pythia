from __future__ import annotations

from urllib.parse import urlparse

from ..models import CompareReport

_STATUS_ICONS = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌", "SKIP": "⏭️ "}
_CATEGORY_WEIGHTS = {"structure": 40, "html": 30, "content": 30}


def _short(url: str) -> str:
    p = urlparse(url)
    label = p.netloc + p.path.rstrip("/")
    return label if label else url


def render_compare_markdown(cmp: CompareReport) -> str:
    r1, r2 = cmp.report1, cmp.report2
    s1, s2 = _short(cmp.url1), _short(cmp.url2)

    delta = cmp.score_delta
    if cmp.leader == "tie":
        verdict = "Tied"
    elif cmp.leader == "url1":
        verdict = f"**{s1}** leads by {abs(delta):.0f} pts"
    else:
        verdict = f"**{s2}** leads by {abs(delta):.0f} pts"

    lines: list[str] = [
        "# Pythia Compare",
        "",
        f"**{cmp.url1}**  ←→  **{cmp.url2}**",
        "",
        f"Score: **{r1.score:.0f}/100** vs **{r2.score:.0f}/100** — {verdict}",
        "",
    ]

    checks1 = {r.name: r for r in r1.results}
    checks2 = {r.name: r for r in r2.results}

    for category in ("structure", "html", "content"):
        cat1 = r1.scores_by_category.get(category, 0.0)
        cat2 = r2.scores_by_category.get(category, 0.0)
        cat_delta = cat2 - cat1
        sign = "+" if cat_delta > 0 else ""
        weight = _CATEGORY_WEIGHTS[category]

        header = f"## {category.upper()} ({weight}%)  —  {cat1:.0f}/100 vs {cat2:.0f}/100  (Δ {sign}{cat_delta:.0f})"
        lines += [header, ""]

        col1_w = max(len(s1), 10)
        col2_w = max(len(s2), 10)
        lines.append(f"| {'Check':<30} | {s1:<{col1_w}} | {s2:<{col2_w}} |")
        lines.append(f"|{'-' * 32}|{'-' * (col1_w + 2)}|{'-' * (col2_w + 2)}|")

        names = [r.name for r in r1.results if r.category == category]
        for name in names:
            c1 = checks1.get(name)
            c2 = checks2.get(name)
            i1 = _STATUS_ICONS.get(c1.status, "?") if c1 else "?"
            i2 = _STATUS_ICONS.get(c2.status, "?") if c2 else "?"
            st1 = c1.status if c1 else "?"
            st2 = c2.status if c2 else "?"
            lines.append(f"| `{name:<28}` | {i1} {st1:<{col1_w - 3}} | {i2} {st2:<{col2_w - 3}} |")

        lines.append("")

    return "\n".join(lines)


def render_compare_json(cmp: CompareReport) -> str:
    return cmp.model_dump_json(indent=2)
