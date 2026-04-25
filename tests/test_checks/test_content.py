"""Tests for content checks (checks 11–15)."""
import pytest

from pythia.checks.content import EeatSignals, FaqPattern, GenericHeadings, StructuredContent, WordCount
from pythia.models import AuditContext


def _ctx(html: str, url: str = "https://example.com/article", page_type: str = "auto") -> AuditContext:
    c = AuditContext(url=url, html=html, page_type=page_type)  # type: ignore[arg-type]
    c.get_soup()
    return c


def _homepage_ctx(html: str) -> AuditContext:
    return _ctx(html, url="https://example.com/", page_type="auto")


# ── generic_headings ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generic_headings_pass(ctx):
    result = await GenericHeadings().run(ctx)
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_generic_headings_fail_h1_welcome():
    # "Welcome" as H1 → FAIL
    c = _ctx("<html><body><h1>Welcome</h1><h2>Section</h2></body></html>")
    result = await GenericHeadings().run(c)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_generic_headings_fail_h1_home(ctx_bad):
    # ctx_bad has <h1>Welcome</h1> → FAIL
    result = await GenericHeadings().run(ctx_bad)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_generic_headings_warn_h2_home():
    c = _ctx("<html><body><h1>Real Title</h1><h2>Home</h2><h2>Section</h2></body></html>")
    result = await GenericHeadings().run(c)
    assert result.status == "WARN"
    assert result.details["generic_headings"][0]["tag"] == "h2"


@pytest.mark.asyncio
async def test_generic_headings_fail_three_generic():
    c = _ctx(
        "<html><body>"
        "<h1>Real Title</h1>"
        "<h2>Home</h2><h2>Welcome</h2><h2>Page</h2>"
        "</body></html>"
    )
    result = await GenericHeadings().run(c)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_generic_headings_case_insensitive():
    c = _ctx("<html><body><h1>WELCOME</h1></body></html>")
    result = await GenericHeadings().run(c)
    assert result.status == "FAIL"


# ── faq_pattern ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_faq_pass_dl_element(ctx):
    # ctx (good_page) has a <dl>
    result = await FaqPattern().run(ctx)
    assert result.status == "PASS"
    assert result.details["method"] == "dl_element"


@pytest.mark.asyncio
async def test_faq_pass_details_summary():
    c = _ctx(
        "<html><body>"
        "<details><summary>What is this?</summary><p>An answer.</p></details>"
        "</body></html>"
    )
    result = await FaqPattern().run(c)
    assert result.status == "PASS"
    assert result.details["method"] == "details_summary"


@pytest.mark.asyncio
async def test_faq_pass_schema_faqpage():
    c = _ctx(
        '<html><body itemscope itemtype="https://schema.org/FAQPage">'
        "<p>Q and A content</p></body></html>"
    )
    result = await FaqPattern().run(c)
    assert result.status == "PASS"
    assert result.details["method"] == "microdata_faqpage"


@pytest.mark.asyncio
async def test_faq_pass_jsonld_faqpage():
    c = _ctx(
        '<html><head>'
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"FAQPage"}'
        '</script>'
        "</head><body></body></html>"
    )
    result = await FaqPattern().run(c)
    assert result.status == "PASS"
    assert result.details["method"] == "jsonld_faqpage"


@pytest.mark.asyncio
async def test_faq_warn_absent(ctx_bad):
    result = await FaqPattern().run(ctx_bad)
    assert result.status == "WARN"


# ── eeat_signals ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_eeat_pass_author_and_date(ctx):
    # ctx (good_page) has <span class="author"> and <time>
    result = await EeatSignals().run(ctx)
    assert result.status == "PASS"
    assert result.details["has_author"] is True
    assert result.details["has_date"] is True


@pytest.mark.asyncio
async def test_eeat_fail_neither(ctx_bad):
    result = await EeatSignals().run(ctx_bad)
    assert result.status == "FAIL"
    assert result.details["has_author"] is False
    assert result.details["has_date"] is False


@pytest.mark.asyncio
async def test_eeat_warn_date_only():
    c = _ctx("<html><body><time datetime='2024-01-01'>Jan 1</time></body></html>")
    result = await EeatSignals().run(c)
    assert result.status == "WARN"
    assert result.details["has_date"] is True
    assert result.details["has_author"] is False


@pytest.mark.asyncio
async def test_eeat_warn_author_only():
    c = _ctx('<html><body><span class="author">Jane Smith</span></body></html>')
    result = await EeatSignals().run(c)
    assert result.status == "WARN"
    assert result.details["has_author"] is True
    assert result.details["has_date"] is False


@pytest.mark.asyncio
async def test_eeat_pass_itemprop_author():
    c = _ctx(
        '<html><body>'
        '<span itemprop="author">John Doe</span>'
        '<time datetime="2024-03-01">March 2024</time>'
        "</body></html>"
    )
    result = await EeatSignals().run(c)
    assert result.status == "PASS"


# ── structured_content ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_structured_content_pass_ul(ctx):
    result = await StructuredContent().run(ctx)
    assert result.status == "PASS"
    assert result.details["has_ul"] is True


@pytest.mark.asyncio
async def test_structured_content_pass_table():
    c = _ctx("<html><body><table><tr><td>Data</td></tr></table></body></html>")
    result = await StructuredContent().run(c)
    assert result.status == "PASS"
    assert result.details["has_table"] is True


@pytest.mark.asyncio
async def test_structured_content_pass_ol():
    c = _ctx("<html><body><ol><li>One</li><li>Two</li></ol></body></html>")
    result = await StructuredContent().run(c)
    assert result.status == "PASS"
    assert result.details["has_ol"] is True


@pytest.mark.asyncio
async def test_structured_content_fail_none(ctx_bad):
    result = await StructuredContent().run(ctx_bad)
    assert result.status == "FAIL"
    assert result.details["has_ul"] is False
    assert result.details["has_ol"] is False
    assert result.details["has_table"] is False


# ── page-type awareness (faq + eeat) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_faq_skip_for_homepage():
    c = _homepage_ctx("<html><body><p>Welcome</p></body></html>")
    result = await FaqPattern().run(c)
    assert result.status == "SKIP"


@pytest.mark.asyncio
async def test_eeat_skip_for_homepage():
    c = _homepage_ctx("<html><body><p>Welcome</p></body></html>")
    result = await EeatSignals().run(c)
    assert result.status == "SKIP"


@pytest.mark.asyncio
async def test_faq_not_skip_for_explicit_article():
    c = _ctx("<html><body><p>No FAQ here.</p></body></html>", page_type="article")
    result = await FaqPattern().run(c)
    assert result.status == "WARN"


@pytest.mark.asyncio
async def test_eeat_not_skip_for_explicit_article():
    c = _ctx("<html><body><p>No signals.</p></body></html>", page_type="article")
    result = await EeatSignals().run(c)
    assert result.status == "FAIL"


# ── word_count ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_word_count_pass():
    words = " ".join(["content"] * 320)
    c = _ctx(f"<html><body><article><p>{words}</p></article></body></html>")
    result = await WordCount().run(c)
    assert result.status == "PASS"
    assert result.details["word_count"] >= 300


@pytest.mark.asyncio
async def test_word_count_fail_too_short():
    c = _ctx("<html><body><p>Short page.</p></body></html>")
    result = await WordCount().run(c)
    assert result.status == "FAIL"
    assert result.details["word_count"] < 100


@pytest.mark.asyncio
async def test_word_count_warn_medium():
    words = " ".join(["word"] * 150)
    c = _ctx(f"<html><body><p>{words}</p></body></html>")
    result = await WordCount().run(c)
    assert result.status == "WARN"
    assert 100 <= result.details["word_count"] < 300


@pytest.mark.asyncio
async def test_word_count_skip_homepage():
    c = _homepage_ctx("<html><body><p>Welcome to our homepage.</p></body></html>")
    result = await WordCount().run(c)
    assert result.status == "SKIP"


@pytest.mark.asyncio
async def test_word_count_excludes_nav_and_script():
    # nav + script content should not count toward word count
    nav_words = " ".join(["navword"] * 500)
    body_words = " ".join(["realword"] * 50)
    html = (
        f"<html><body>"
        f"<nav>{nav_words}</nav>"
        f"<script>var x = 1;</script>"
        f"<article><p>{body_words}</p></article>"
        f"</body></html>"
    )
    c = _ctx(html)
    result = await WordCount().run(c)
    assert result.details["word_count"] < 100  # only real content counted
