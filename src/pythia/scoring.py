from __future__ import annotations

from .models import CheckResult, Report

CATEGORY_WEIGHTS: dict[str, float] = {
    "structure": 0.40,
    "html": 0.30,
    "content": 0.30,
}


def score_results(results: list[CheckResult]) -> tuple[float, dict[str, float]]:
    by_category: dict[str, list[CheckResult]] = {"structure": [], "html": [], "content": []}
    for r in results:
        if r.category in by_category:
            by_category[r.category].append(r)

    scores_by_category: dict[str, float] = {}
    for category, checks in by_category.items():
        eligible = [r for r in checks if r.status != "SKIP"]
        if not eligible:
            scores_by_category[category] = 0.0
            continue
        total_weight = sum(r.weight for r in eligible)
        weighted_sum = sum(r.score * r.weight for r in eligible)
        scores_by_category[category] = weighted_sum / total_weight if total_weight else 0.0

    global_score = sum(
        scores_by_category.get(cat, 0.0) * weight
        for cat, weight in CATEGORY_WEIGHTS.items()
    )
    return global_score, scores_by_category


def build_report(
    url: str,
    results: list[CheckResult],
    threshold: int = 70,
    lang: str = "en",
) -> Report:
    score, scores_by_category = score_results(results)
    return Report(
        url=url,
        lang=lang,  # type: ignore[arg-type]
        score=round(score, 1),
        threshold=threshold,
        passed=score >= threshold,
        results=results,
        scores_by_category={k: round(v, 1) for k, v in scores_by_category.items()},
    )
