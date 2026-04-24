import pytest

from pythia.models import CheckResult
from pythia.scoring import build_report, score_results


def _r(category: str, status: str, weight: float = 1.0) -> CheckResult:
    score = {"PASS": 100, "WARN": 50, "FAIL": 0, "SKIP": 0}[status]
    return CheckResult(
        name="test", category=category, status=status, score=score, weight=weight, message=""  # type: ignore[arg-type]
    )


def test_all_pass():
    results = [_r("structure", "PASS"), _r("html", "PASS"), _r("content", "PASS")]
    score, _ = score_results(results)
    assert score == 100.0


def test_all_fail():
    results = [_r("structure", "FAIL"), _r("html", "FAIL"), _r("content", "FAIL")]
    score, _ = score_results(results)
    assert score == 0.0


def test_warn_score():
    results = [_r("structure", "WARN"), _r("html", "PASS"), _r("content", "PASS")]
    score, by_cat = score_results(results)
    assert by_cat["structure"] == 50.0
    assert by_cat["html"] == 100.0
    # 50*0.4 + 100*0.3 + 100*0.3 = 20 + 30 + 30 = 80
    assert score == pytest.approx(80.0)


def test_skip_excluded_from_category():
    results = [_r("structure", "SKIP"), _r("html", "PASS"), _r("content", "PASS")]
    score, by_cat = score_results(results)
    assert by_cat["structure"] == 0.0
    # 0*0.4 + 100*0.3 + 100*0.3 = 60
    assert score == pytest.approx(60.0)


def test_category_weight_structure_only():
    results = [_r("structure", "PASS"), _r("html", "FAIL"), _r("content", "FAIL")]
    score, _ = score_results(results)
    assert score == pytest.approx(40.0)


def test_weight_intra_category():
    # One check weight=2.0 PASS, one check weight=1.0 FAIL → weighted avg = (200+0)/3 = 66.7
    results = [
        CheckResult(name="a", category="html", status="PASS", score=100, weight=2.0, message=""),
        CheckResult(name="b", category="html", status="FAIL", score=0, weight=1.0, message=""),
    ]
    _, by_cat = score_results(results)
    assert by_cat["html"] == pytest.approx(100 * 2 / 3, rel=1e-3)


def test_build_report_passed():
    results = [_r("structure", "PASS"), _r("html", "PASS"), _r("content", "PASS")]
    report = build_report("https://example.com", results, threshold=70)
    assert report.passed
    assert report.score == 100.0
    assert report.url == "https://example.com"


def test_build_report_failed():
    results = [_r("structure", "FAIL"), _r("html", "FAIL"), _r("content", "FAIL")]
    report = build_report("https://example.com", results, threshold=70)
    assert not report.passed
    assert report.score == 0.0


def test_build_report_threshold_boundary():
    # structure PASS (40) + html FAIL (0) + content PASS (30) = 70 → exactly threshold
    results = [_r("structure", "PASS"), _r("html", "FAIL"), _r("content", "PASS")]
    report = build_report("https://example.com", results, threshold=70)
    assert report.score == pytest.approx(70.0)
    assert report.passed  # >= threshold


def test_empty_category_scores_zero():
    results = [_r("html", "PASS")]
    _, by_cat = score_results(results)
    assert by_cat["structure"] == 0.0
    assert by_cat["content"] == 0.0
