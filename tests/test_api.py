"""Tests for the public Python API (audit_url / audit_html / fix_url / compare_urls)."""

import httpx
import pytest
import respx

from pythia import CheckResult, Fix, FixReport, Report, audit_html, audit_url, fix_url

_ARTICLE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <title>How to Write Good Content for AI</title>
  <meta name="description" content="A practical guide to writing content that AI systems can understand.">
  <meta property="og:title" content="How to Write Good Content">
  <meta property="og:description" content="Practical guide.">
  <meta property="og:type" content="article">
  <link rel="canonical" href="https://example.com/article">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"Article","name":"How to Write Good Content"}
  </script>
</head>
<body>
  <h1>How to Write Good Content for AI</h1>
  <p>By <span class="author">Jane Smith</span> — <time datetime="2024-03-01">March 2024</time></p>
  <h2>Introduction</h2>
  <ul><li>Be clear</li><li>Be structured</li></ul>
  <h2>Details</h2>
  <dl><dt>Question?</dt><dd>Answer.</dd></dl>
</body>
</html>"""


# ── audit_html ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_html_returns_report():
    report = await audit_html(_ARTICLE_HTML, base_url="https://example.com/article")
    assert isinstance(report, Report)
    assert report.url == "https://example.com/article"
    assert isinstance(report.score, float)
    assert isinstance(report.results, list)
    assert len(report.results) > 0


@pytest.mark.asyncio
async def test_audit_html_result_types():
    report = await audit_html(_ARTICLE_HTML)
    for r in report.results:
        assert isinstance(r, CheckResult)
        assert r.status in ("PASS", "WARN", "FAIL", "SKIP")
        assert r.score in (0, 50, 100)


@pytest.mark.asyncio
async def test_audit_html_no_base_url_structure_checks_skip():
    report = await audit_html(_ARTICLE_HTML, base_url="")
    structure_results = [r for r in report.results if r.category == "structure"]
    # llms_txt, llms_full_txt, sitemap require a base URL — should SKIP
    skip_names = {r.name for r in structure_results if r.status == "SKIP"}
    assert "llms_txt_present" in skip_names
    assert "llms_full_txt_present" in skip_names
    assert "sitemap_accessible" in skip_names


@pytest.mark.asyncio
async def test_audit_html_label_without_base_url():
    report = await audit_html("<html><body><h1>Hi</h1></body></html>")
    assert report.url == "<html>"


@pytest.mark.asyncio
async def test_audit_html_html_checks_work_offline():
    # base_url with a path → detected as article, all content/html checks run
    report = await audit_html(_ARTICLE_HTML, base_url="https://example.com/article")
    by_name = {r.name: r for r in report.results}
    assert by_name["single_h1"].status == "PASS"
    assert by_name["eeat_signals"].status == "PASS"
    assert by_name["faq_pattern"].status == "PASS"
    assert by_name["canonical_url"].status == "PASS"


@pytest.mark.asyncio
async def test_audit_html_page_type_homepage():
    report = await audit_html(_ARTICLE_HTML, base_url="https://example.com/")
    assert report.page_type == "homepage"
    by_name = {r.name: r for r in report.results}
    assert by_name["eeat_signals"].status == "SKIP"
    assert by_name["faq_pattern"].status == "SKIP"
    assert by_name["word_count"].status == "SKIP"


@pytest.mark.asyncio
async def test_audit_html_threshold_pass():
    report = await audit_html(_ARTICLE_HTML, base_url="https://example.com/article", threshold=30)
    assert report.threshold == 30
    assert report.passed is True


@pytest.mark.asyncio
async def test_audit_html_threshold_fail():
    report = await audit_html("<html><body></body></html>", threshold=70)
    assert report.passed is False


@pytest.mark.asyncio
async def test_audit_html_lang_fr():
    report = await audit_html(_ARTICLE_HTML, lang="fr")
    assert report.lang == "fr"
    # French i18n messages should be used
    by_name = {r.name: r for r in report.results}
    assert "Exactement" in by_name["single_h1"].message or "trouvé" in by_name["single_h1"].message


# ── audit_url ──────────────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_audit_url_returns_report():
    respx.get("https://example.com/page").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms-full.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))

    report = await audit_url("https://example.com/page")
    assert isinstance(report, Report)
    assert report.url == "https://example.com/page"
    assert report.page_type == "article"


@respx.mock
@pytest.mark.asyncio
async def test_audit_url_homepage_detection():
    respx.get("https://example.com/").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms-full.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))

    report = await audit_url("https://example.com/")
    assert report.page_type == "homepage"


# ── public exports ─────────────────────────────────────────────────────────

def test_public_exports_importable():
    import pythia
    assert hasattr(pythia, "audit_url")
    assert hasattr(pythia, "audit_html")
    assert hasattr(pythia, "Report")
    assert hasattr(pythia, "CheckResult")
    assert hasattr(pythia, "AuditContext")
    assert hasattr(pythia, "__version__")


def test_version_is_string():
    import pythia
    assert isinstance(pythia.__version__, str)
    assert pythia.__version__.startswith("0.")


# ── fix_url ────────────────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_fix_url_returns_fix_report():
    respx.get("https://example.com/page").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms-full.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))

    fix_report = await fix_url("https://example.com/page")
    assert isinstance(fix_report, FixReport)
    assert fix_report.url == "https://example.com/page"
    assert isinstance(fix_report.audit, Report)
    assert isinstance(fix_report.fixes, list)
    assert all(isinstance(f, Fix) for f in fix_report.fixes)


@respx.mock
@pytest.mark.asyncio
async def test_fix_url_only_fail_warn():
    respx.get("https://example.com/page").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/llms-full.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))

    fix_report = await fix_url("https://example.com/page")
    for fix in fix_report.fixes:
        assert fix.status in ("FAIL", "WARN")
