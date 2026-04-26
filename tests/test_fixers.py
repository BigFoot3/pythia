"""Tests for pythia.fixers — generate_fixes() and individual fix generators."""
from __future__ import annotations

import json

from pythia.fixers import _make_fix, generate_fixes
from pythia.models import CheckResult, Fix, Report

# ── helpers ───────────────────────────────────────────────────────────────

def _result(name: str, status: str, details: dict | None = None, category: str = "html") -> CheckResult:
    return CheckResult(
        name=name,
        category=category,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        score={"PASS": 100, "WARN": 50, "FAIL": 0, "SKIP": 0}[status],
        weight=1.0,
        message="",
        details=details or {},
    )


def _minimal_report(results: list[CheckResult]) -> Report:
    return Report(
        url="https://example.com/page",
        score=50.0,
        threshold=70,
        passed=False,
        results=results,
        scores_by_category={},
    )


# ── generate_fixes filtering ──────────────────────────────────────────────

def test_generate_fixes_skips_pass():
    report = _minimal_report([_result("single_h1", "PASS")])
    assert generate_fixes(report) == []


def test_generate_fixes_skips_skip():
    report = _minimal_report([_result("word_count", "SKIP", category="content")])
    assert generate_fixes(report) == []


def test_generate_fixes_includes_fail():
    report = _minimal_report([_result("single_h1", "FAIL", {"h1_count": 0})])
    fixes = generate_fixes(report)
    assert len(fixes) == 1
    assert fixes[0].check_name == "single_h1"


def test_generate_fixes_includes_warn():
    report = _minimal_report([_result("canonical_url", "WARN")])
    fixes = generate_fixes(report)
    assert len(fixes) == 1
    assert fixes[0].check_name == "canonical_url"


def test_generate_fixes_multiple_results():
    report = _minimal_report([
        _result("single_h1", "PASS"),
        _result("canonical_url", "WARN"),
        _result("meta_description", "FAIL"),
        _result("title_length", "SKIP"),
    ])
    fixes = generate_fixes(report)
    assert len(fixes) == 2
    names = {f.check_name for f in fixes}
    assert names == {"canonical_url", "meta_description"}


# ── structure checks ──────────────────────────────────────────────────────

def test_fix_llms_txt_fail():
    fix = _make_fix(_result("llms_txt_present", "FAIL", category="structure"), "https://example.com")
    assert fix is not None
    assert fix.location == "server"
    assert "llms.txt" in fix.snippet


def test_fix_llms_full_txt_warn():
    fix = _make_fix(_result("llms_full_txt_present", "WARN", category="structure"), "https://example.com")
    assert fix is not None
    assert fix.location == "server"
    assert "llms-full.txt" in fix.snippet


def test_fix_robots_ai_bots_fail():
    fix = _make_fix(
        _result("robots_ai_bots", "FAIL", {"blocked_bots": ["GPTBot", "ClaudeBot"]}, "structure"),
        "https://example.com",
    )
    assert fix is not None
    assert fix.location == "server"
    assert "GPTBot" in fix.snippet
    assert "ClaudeBot" in fix.snippet


def test_fix_sitemap_fail():
    fix = _make_fix(_result("sitemap_accessible", "FAIL", category="structure"), "https://example.com")
    assert fix is not None
    assert fix.location == "server"
    assert "sitemap.xml" in fix.snippet


# ── head checks ───────────────────────────────────────────────────────────

def test_fix_jsonld_fail():
    fix = _make_fix(_result("jsonld_present_valid", "FAIL", category="structure"), "https://example.com/page")
    assert fix is not None
    assert fix.location == "head"
    assert "application/ld+json" in fix.snippet
    assert "https://example.com/page" in fix.snippet


def test_fix_jsonld_warn():
    fix = _make_fix(_result("jsonld_present_valid", "WARN", category="structure"), "https://example.com")
    assert fix is not None
    assert fix.location == "head"
    assert fix.note  # should have a note pointing to validator


def test_fix_title_fail():
    fix = _make_fix(_result("title_length", "FAIL"), "https://example.com")
    assert fix is not None
    assert fix.location == "head"
    assert "<title>" in fix.snippet


def test_fix_title_warn_too_short():
    fix = _make_fix(_result("title_length", "WARN", {"length": 10}), "https://example.com")
    assert fix is not None
    assert fix.location == "head"
    assert "Expand" in fix.snippet
    assert "10" in fix.note


def test_fix_title_warn_too_long():
    fix = _make_fix(_result("title_length", "WARN", {"length": 80}), "https://example.com")
    assert fix is not None
    assert "Shorten" in fix.snippet
    assert "80" in fix.note


def test_fix_meta_description_fail():
    fix = _make_fix(_result("meta_description", "FAIL"), "https://example.com")
    assert fix is not None
    assert fix.location == "head"
    assert 'name="description"' in fix.snippet


def test_fix_meta_description_warn_short():
    fix = _make_fix(_result("meta_description", "WARN", {"length": 30}), "https://example.com")
    assert fix is not None
    assert "Expand" in fix.snippet


def test_fix_meta_description_warn_long():
    fix = _make_fix(_result("meta_description", "WARN", {"length": 180}), "https://example.com")
    assert fix is not None
    assert "Shorten" in fix.snippet


def test_fix_opengraph_fail_all_missing():
    fix = _make_fix(
        _result("opengraph_minimal", "FAIL", {"missing": ["og:title", "og:description", "og:type"]}),
        "https://example.com",
    )
    assert fix is not None
    assert fix.location == "head"
    assert "og:title" in fix.snippet
    assert "og:description" in fix.snippet
    assert "og:type" in fix.snippet


def test_fix_opengraph_warn_partial():
    fix = _make_fix(
        _result("opengraph_minimal", "WARN", {"found": ["og:title"], "missing": ["og:description", "og:type"]}),
        "https://example.com",
    )
    assert fix is not None
    assert "og:title" not in fix.snippet
    assert "og:description" in fix.snippet
    assert "og:type" in fix.snippet


def test_fix_canonical_warn():
    fix = _make_fix(_result("canonical_url", "WARN"), "https://example.com/page")
    assert fix is not None
    assert fix.location == "head"
    assert 'rel="canonical"' in fix.snippet
    assert "https://example.com/page" in fix.snippet


# ── body checks ───────────────────────────────────────────────────────────

def test_fix_single_h1_fail():
    fix = _make_fix(_result("single_h1", "FAIL", {"h1_count": 0}), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "<h1>" in fix.snippet


def test_fix_single_h1_warn():
    fix = _make_fix(_result("single_h1", "WARN", {"h1_count": 3}), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "2" in fix.snippet  # remove 2 extra


def test_fix_heading_hierarchy_fail():
    fix = _make_fix(_result("heading_hierarchy", "FAIL", {"gaps": [(1, 3)]}), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "H1" in fix.snippet
    assert "H3" in fix.snippet


def test_fix_heading_hierarchy_no_gaps_returns_none():
    fix = _make_fix(_result("heading_hierarchy", "FAIL", {"gaps": []}), "https://example.com")
    assert fix is None


def test_fix_generic_headings():
    details = {"generic_headings": [{"tag": "h1", "text": "Home"}]}
    fix = _make_fix(_result("generic_headings", "FAIL", details), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "Home" in fix.snippet


def test_fix_faq_pattern_warn():
    fix = _make_fix(_result("faq_pattern", "WARN", category="content"), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "<dl>" in fix.snippet
    assert "<dt>" in fix.snippet


def test_fix_eeat_no_author_no_date():
    fix = _make_fix(
        _result("eeat_signals", "FAIL", {"has_author": False, "has_date": False}, "content"),
        "https://example.com",
    )
    assert fix is not None
    assert fix.location == "body"
    assert 'itemprop="author"' in fix.snippet
    assert 'itemprop="datePublished"' in fix.snippet


def test_fix_eeat_no_author_only():
    fix = _make_fix(
        _result("eeat_signals", "WARN", {"has_author": False, "has_date": True}, "content"),
        "https://example.com",
    )
    assert fix is not None
    assert 'itemprop="author"' in fix.snippet
    assert "datePublished" not in fix.snippet


def test_fix_eeat_no_date_only():
    fix = _make_fix(
        _result("eeat_signals", "WARN", {"has_author": True, "has_date": False}, "content"),
        "https://example.com",
    )
    assert fix is not None
    assert "datePublished" in fix.snippet
    assert 'itemprop="author"' not in fix.snippet


def test_fix_structured_content_fail():
    fix = _make_fix(_result("structured_content", "FAIL", category="content"), "https://example.com")
    assert fix is not None
    assert fix.location == "body"
    assert "<ul>" in fix.snippet


# ── content check ─────────────────────────────────────────────────────────

def test_fix_word_count_fail():
    fix = _make_fix(
        _result("word_count", "FAIL", {"word_count": 50, "min_recommended": 300}, "content"),
        "https://example.com",
    )
    assert fix is not None
    assert fix.location == "content"
    assert "250" in fix.snippet  # 300 - 50 = 250 more words needed
    assert "50" in fix.note


def test_fix_word_count_warn():
    fix = _make_fix(
        _result("word_count", "WARN", {"word_count": 150, "min_recommended": 300}, "content"),
        "https://example.com",
    )
    assert fix is not None
    assert "150" in fix.snippet  # 300 - 150 = 150 more words needed


# ── unknown check ─────────────────────────────────────────────────────────

def test_fix_unknown_check_returns_none():
    fix = _make_fix(_result("nonexistent_check", "FAIL"), "https://example.com")
    assert fix is None


# ── Fix model ─────────────────────────────────────────────────────────────

def test_fix_is_pydantic_serializable():
    fix = Fix(check_name="canonical_url", status="WARN", location="head",
              snippet='<link rel="canonical" href="https://example.com">',
              note="")
    data = fix.model_dump()
    assert data["check_name"] == "canonical_url"
    assert data["location"] == "head"
    fix2 = Fix.model_validate(data)
    assert fix2 == fix


# ── renderers ─────────────────────────────────────────────────────────────

def test_render_fixes_markdown_no_fixes():
    from pythia.reporters.fixes import render_fixes_markdown
    report = _minimal_report([_result("single_h1", "PASS")])
    out = render_fixes_markdown(report, [])
    assert "No fixes needed" in out
    assert "https://example.com" in out


def test_render_fixes_markdown_with_fixes():
    from pythia.reporters.fixes import render_fixes_markdown
    report = _minimal_report([_result("canonical_url", "WARN")])
    fixes = generate_fixes(report)
    out = render_fixes_markdown(report, fixes)
    assert "canonical_url" in out
    assert "Add to <head>" in out
    assert "```html" in out


def test_render_fixes_markdown_sections_ordered():
    from pythia.reporters.fixes import render_fixes_markdown
    report = _minimal_report([
        _result("canonical_url", "WARN"),            # head
        _result("single_h1", "FAIL", {"h1_count": 0}),  # body
        _result("llms_txt_present", "FAIL", category="structure"),  # server
    ])
    fixes = generate_fixes(report)
    out = render_fixes_markdown(report, fixes)
    head_pos = out.index("Add to <head>")
    body_pos = out.index("Add to <body>")
    server_pos = out.index("Server-side actions")
    assert head_pos < body_pos < server_pos


def test_render_fixes_json():
    from pythia.reporters.fixes import render_fixes_json
    report = _minimal_report([_result("canonical_url", "WARN")])
    fixes = generate_fixes(report)
    out = render_fixes_json(report, fixes)
    data = json.loads(out)
    assert data["url"] == "https://example.com/page"
    assert data["fixes_count"] == 1
    assert data["fixes"][0]["check_name"] == "canonical_url"
    assert data["fixes"][0]["location"] == "head"
