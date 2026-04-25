"""Tests for HTML checks (checks 6–10 + canonical_url)."""
import pytest

from pythia.checks.html import (
    CanonicalUrl,
    HeadingHierarchy,
    MetaDescription,
    OpenGraphMinimal,
    SingleH1,
    TitleLength,
)
from pythia.models import AuditContext


def _ctx(html: str) -> AuditContext:
    c = AuditContext(url="https://example.com", html=html)
    c.get_soup()
    return c


# ── single_h1 ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_single_h1_pass(ctx):
    result = await SingleH1().run(ctx)
    assert result.status == "PASS"
    assert result.details["h1_count"] == 1


@pytest.mark.asyncio
async def test_single_h1_fail_missing():
    c = _ctx("<html><body><h2>Section</h2></body></html>")
    result = await SingleH1().run(c)
    assert result.status == "FAIL"
    assert result.details["h1_count"] == 0


@pytest.mark.asyncio
async def test_single_h1_warn_multiple(ctx_bad):
    result = await SingleH1().run(ctx_bad)
    assert result.status == "WARN"
    assert result.details["h1_count"] == 2


# ── heading_hierarchy ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_heading_hierarchy_pass(ctx):
    result = await HeadingHierarchy().run(ctx)
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_heading_hierarchy_fail_h1_to_h3(ctx_bad):
    # bad page: h1 → h1 → h3 (gap h1→h3)
    result = await HeadingHierarchy().run(ctx_bad)
    assert result.status == "FAIL"
    assert (1, 3) in result.details["gaps"]


@pytest.mark.asyncio
async def test_heading_hierarchy_fail_h2_to_h4():
    c = _ctx("<html><body><h1>T</h1><h2>A</h2><h4>B</h4></body></html>")
    result = await HeadingHierarchy().run(c)
    assert result.status == "FAIL"
    assert (2, 4) in result.details["gaps"]


@pytest.mark.asyncio
async def test_heading_hierarchy_pass_going_back_up():
    # h1 → h2 → h3 → h2 → h3 is valid
    c = _ctx("<html><body><h1>A</h1><h2>B</h2><h3>C</h3><h2>D</h2><h3>E</h3></body></html>")
    result = await HeadingHierarchy().run(c)
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_heading_hierarchy_pass_no_headings():
    c = _ctx("<html><body><p>Text only</p></body></html>")
    result = await HeadingHierarchy().run(c)
    assert result.status == "PASS"


# ── title_length ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_title_length_pass(ctx):
    # "How to Build a Python CLI Tool in 2024" = 37 chars
    result = await TitleLength().run(ctx)
    assert result.status == "PASS"
    assert 30 <= result.details["length"] <= 65


@pytest.mark.asyncio
async def test_title_length_fail_absent():
    c = _ctx("<html><head></head><body></body></html>")
    result = await TitleLength().run(c)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_title_length_warn_too_short():
    c = _ctx("<html><head><title>Hi</title></head></html>")
    result = await TitleLength().run(c)
    assert result.status == "WARN"
    assert result.details["length"] == 2


@pytest.mark.asyncio
async def test_title_length_warn_too_long():
    long_title = "A" * 70
    c = _ctx(f"<html><head><title>{long_title}</title></head></html>")
    result = await TitleLength().run(c)
    assert result.status == "WARN"
    assert result.details["length"] == 70


@pytest.mark.asyncio
async def test_title_length_pass_boundary_30():
    c = _ctx(f"<html><head><title>{'A' * 30}</title></head></html>")
    result = await TitleLength().run(c)
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_title_length_pass_boundary_65():
    c = _ctx(f"<html><head><title>{'A' * 65}</title></head></html>")
    result = await TitleLength().run(c)
    assert result.status == "PASS"


# ── meta_description ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_meta_description_pass(ctx):
    result = await MetaDescription().run(ctx)
    assert result.status == "PASS"
    assert 70 <= result.details["length"] <= 160


@pytest.mark.asyncio
async def test_meta_description_fail_absent(ctx_bad):
    result = await MetaDescription().run(ctx_bad)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_meta_description_warn_too_short():
    c = _ctx('<html><head><meta name="description" content="Short."></head></html>')
    result = await MetaDescription().run(c)
    assert result.status == "WARN"
    assert result.details["length"] == 6


@pytest.mark.asyncio
async def test_meta_description_warn_too_long():
    long_desc = "A" * 165
    c = _ctx(f'<html><head><meta name="description" content="{long_desc}"></head></html>')
    result = await MetaDescription().run(c)
    assert result.status == "WARN"
    assert result.details["length"] == 165


@pytest.mark.asyncio
async def test_meta_description_pass_boundary_70():
    c = _ctx(f'<html><head><meta name="description" content="{"A" * 70}"></head></html>')
    result = await MetaDescription().run(c)
    assert result.status == "PASS"


# ── opengraph_minimal ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_opengraph_pass_all_three(ctx):
    result = await OpenGraphMinimal().run(ctx)
    assert result.status == "PASS"
    assert set(result.details["found"]) == {"og:title", "og:description", "og:type"}


@pytest.mark.asyncio
async def test_opengraph_fail_none(ctx_bad):
    result = await OpenGraphMinimal().run(ctx_bad)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_opengraph_warn_missing_one():
    c = _ctx(
        '<html><head>'
        '<meta property="og:title" content="T">'
        '<meta property="og:description" content="D">'
        '</head></html>'
    )
    result = await OpenGraphMinimal().run(c)
    assert result.status == "WARN"
    assert "og:type" in result.details["missing"]


@pytest.mark.asyncio
async def test_opengraph_warn_missing_two():
    c = _ctx('<html><head><meta property="og:title" content="T"></head></html>')
    result = await OpenGraphMinimal().run(c)
    assert result.status == "WARN"
    assert len(result.details["missing"]) == 2


# ── canonical_url ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_canonical_url_pass():
    c = _ctx('<html><head><link rel="canonical" href="https://example.com/page"></head></html>')
    result = await CanonicalUrl().run(c)
    assert result.status == "PASS"
    assert result.details["canonical"] == "https://example.com/page"


@pytest.mark.asyncio
async def test_canonical_url_warn_absent(ctx_bad):
    result = await CanonicalUrl().run(ctx_bad)
    assert result.status == "WARN"
    assert result.recommendation is not None


@pytest.mark.asyncio
async def test_canonical_url_warn_empty_href():
    c = _ctx('<html><head><link rel="canonical" href=""></head></html>')
    result = await CanonicalUrl().run(c)
    assert result.status == "WARN"


@pytest.mark.asyncio
async def test_canonical_url_weight():
    assert CanonicalUrl().weight == 0.75
