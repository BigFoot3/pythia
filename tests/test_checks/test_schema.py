"""Tests for JSON-LD check (check 5)."""
import pytest

from pythia.checks.schema import JsonLdPresentValid
from pythia.models import AuditContext


def _ctx(html: str) -> AuditContext:
    c = AuditContext(url="https://example.com", html=html)
    c.get_soup()
    return c


@pytest.mark.asyncio
async def test_jsonld_pass_valid(ctx):
    # ctx (good_page) has valid JSON-LD
    result = await JsonLdPresentValid().run(ctx)
    assert result.status == "PASS"
    assert "Article" in result.details["types"]


@pytest.mark.asyncio
async def test_jsonld_fail_absent(ctx_bad):
    result = await JsonLdPresentValid().run(ctx_bad)
    assert result.status == "FAIL"


@pytest.mark.asyncio
async def test_jsonld_warn_malformed_json():
    c = _ctx(
        '<html><head>'
        '<script type="application/ld+json">{invalid json}</script>'
        "</head></html>"
    )
    result = await JsonLdPresentValid().run(c)
    assert result.status == "WARN"
    assert result.details["invalid_count"] == 1


@pytest.mark.asyncio
async def test_jsonld_pass_multiple_blocks():
    c = _ctx(
        '<html><head>'
        '<script type="application/ld+json">{"@type":"Organization"}</script>'
        '<script type="application/ld+json">{"@type":"Article"}</script>'
        "</head></html>"
    )
    result = await JsonLdPresentValid().run(c)
    assert result.status == "PASS"
    assert result.details["count"] == 2
    assert "Organization" in result.details["types"]


@pytest.mark.asyncio
async def test_jsonld_pass_one_valid_one_invalid():
    c = _ctx(
        '<html><head>'
        '<script type="application/ld+json">{"@type":"Article"}</script>'
        '<script type="application/ld+json">{bad json}</script>'
        "</head></html>"
    )
    result = await JsonLdPresentValid().run(c)
    # One valid → PASS (not WARN)
    assert result.status == "PASS"
    assert result.details["count"] == 1
