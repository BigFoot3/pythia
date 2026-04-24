"""Tests for structure checks (checks 1–4)."""
import httpx
import pytest
import respx

from pythia.checks.structure import (
    LlmsFullTxtPresent,
    LlmsTxtPresent,
    RobotsAiBots,
    SitemapAccessible,
    check_robots_blocked,
)
from pythia.models import AuditContext

BASE = "https://example.com"


def _ctx(robots_txt: str = "", html: str = "") -> AuditContext:
    c = AuditContext(url=BASE, html=html, robots_txt=robots_txt)
    c.get_soup()
    return c


# ── check_robots_blocked (unit tests — no HTTP) ────────────────────────────

def test_robots_blocked_gptbot():
    txt = "User-agent: GPTBot\nDisallow: /\n"
    assert "GPTBot" in check_robots_blocked(txt)


def test_robots_blocked_wildcard_blocks_all():
    txt = "User-agent: *\nDisallow: /\n"
    blocked = check_robots_blocked(txt)
    assert set(blocked) == {"GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "MistralAI-User"}


def test_robots_blocked_partial_path_ok():
    txt = "User-agent: GPTBot\nDisallow: /private\n"
    assert check_robots_blocked(txt) == []


def test_robots_blocked_multiple_agents():
    txt = "User-agent: GPTBot\nUser-agent: ClaudeBot\nDisallow: /\n"
    blocked = check_robots_blocked(txt)
    assert "GPTBot" in blocked
    assert "ClaudeBot" in blocked


def test_robots_blocked_two_separate_blocks():
    txt = "User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n"
    blocked = check_robots_blocked(txt)
    assert "GPTBot" in blocked
    # wildcard block only has Allow: / → no block
    assert len(blocked) == 1


def test_robots_blocked_allow_only():
    txt = "User-agent: *\nAllow: /\n"
    assert check_robots_blocked(txt) == []


# ── RobotsAiBots ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_robots_ai_bots_pass():
    c = _ctx(robots_txt="User-agent: *\nAllow: /\n")
    result = await RobotsAiBots().run(c)
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_robots_ai_bots_fail_gptbot_blocked():
    c = _ctx(robots_txt="User-agent: GPTBot\nDisallow: /\n")
    result = await RobotsAiBots().run(c)
    assert result.status == "FAIL"
    assert "GPTBot" in result.details["blocked_bots"]


@pytest.mark.asyncio
async def test_robots_ai_bots_fail_claudebot_blocked():
    c = _ctx(robots_txt="User-agent: ClaudeBot\nDisallow: /\n")
    result = await RobotsAiBots().run(c)
    assert result.status == "FAIL"
    assert "ClaudeBot" in result.details["blocked_bots"]


@pytest.mark.asyncio
async def test_robots_ai_bots_warn_no_robots_txt():
    c = _ctx(robots_txt="")
    result = await RobotsAiBots().run(c)
    assert result.status == "WARN"


# ── LlmsTxtPresent ────────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_llms_txt_pass():
    respx.get(f"{BASE}/llms.txt").mock(return_value=httpx.Response(200, text="# llms.txt\nSome content"))
    result = await LlmsTxtPresent().run(_ctx())
    assert result.status == "PASS"
    assert result.details["size"] > 0


@respx.mock
@pytest.mark.asyncio
async def test_llms_txt_fail_missing():
    respx.get(f"{BASE}/llms.txt").mock(return_value=httpx.Response(404))
    result = await LlmsTxtPresent().run(_ctx())
    assert result.status == "FAIL"


@respx.mock
@pytest.mark.asyncio
async def test_llms_txt_fail_empty():
    respx.get(f"{BASE}/llms.txt").mock(return_value=httpx.Response(200, text="   "))
    result = await LlmsTxtPresent().run(_ctx())
    assert result.status == "FAIL"


# ── LlmsFullTxtPresent ────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_llms_full_txt_pass():
    respx.get(f"{BASE}/llms-full.txt").mock(return_value=httpx.Response(200, text="Full content here"))
    result = await LlmsFullTxtPresent().run(_ctx())
    assert result.status == "PASS"


@respx.mock
@pytest.mark.asyncio
async def test_llms_full_txt_warn_missing():
    respx.get(f"{BASE}/llms-full.txt").mock(return_value=httpx.Response(404))
    result = await LlmsFullTxtPresent().run(_ctx())
    assert result.status == "WARN"


# ── SitemapAccessible ─────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_sitemap_pass_direct():
    respx.get(f"{BASE}/sitemap.xml").mock(return_value=httpx.Response(200, text="<urlset/>"))
    result = await SitemapAccessible().run(_ctx())
    assert result.status == "PASS"
    assert result.details["source"] == "direct"


@respx.mock
@pytest.mark.asyncio
async def test_sitemap_pass_via_robots():
    robots = f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap-custom.xml\n"
    respx.get(f"{BASE}/sitemap-custom.xml").mock(return_value=httpx.Response(200, text="<urlset/>"))
    result = await SitemapAccessible().run(_ctx(robots_txt=robots))
    assert result.status == "PASS"
    assert result.details["source"] == "robots.txt"


@respx.mock
@pytest.mark.asyncio
async def test_sitemap_fail():
    respx.get(f"{BASE}/sitemap.xml").mock(return_value=httpx.Response(404))
    result = await SitemapAccessible().run(_ctx())
    assert result.status == "FAIL"
