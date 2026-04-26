"""Tests for compare_urls() and the compare renderers."""
from __future__ import annotations

import json

import httpx
import pytest
import respx
from typer.testing import CliRunner

from pythia.api import compare_urls
from pythia.cli import app
from pythia.models import CompareReport
from pythia.reporters.compare import _short, render_compare_json, render_compare_markdown

_HTML_GOOD = """\
<!DOCTYPE html><html lang="en"><head>
  <title>Site A — Best Python CLI Guide (2024)</title>
  <meta name="description" content="A comprehensive guide to Python CLI tools: typer, packaging, distribution.">
  <meta property="og:title" content="Site A CLI Guide">
  <meta property="og:description" content="CLI guide.">
  <meta property="og:type" content="article">
  <link rel="canonical" href="https://site-a.com/guide">
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","name":"Guide"}</script>
</head><body>
  <h1>Best Python CLI Guide</h1>
  <p>By <span class="author">Alice</span> — <time datetime="2024-01-01">Jan 2024</time></p>
  <ul><li>item</li></ul>
  <dl><dt>Q?</dt><dd>A.</dd></dl>
  <p>""" + "word " * 300 + """</p>
</body></html>"""

_HTML_BAD = """\
<!DOCTYPE html><html><head>
  <title>Hi</title>
</head><body>
  <h1>Welcome</h1>
  <p>Short.</p>
</body></html>"""


# ── helpers ───────────────────────────────────────────────────────────────

def _mock_site(url: str, html: str) -> None:
    from urllib.parse import urlparse
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    respx.get(url).mock(return_value=httpx.Response(200, text=html))
    respx.get(f"{base}/robots.txt").mock(return_value=httpx.Response(404))
    respx.get(f"{base}/llms.txt").mock(return_value=httpx.Response(404))
    respx.get(f"{base}/llms-full.txt").mock(return_value=httpx.Response(404))
    respx.get(f"{base}/sitemap.xml").mock(return_value=httpx.Response(404))


# ── _short helper ─────────────────────────────────────────────────────────

def test_short_strips_trailing_slash():
    assert _short("https://example.com/") == "example.com"


def test_short_keeps_path():
    assert _short("https://example.com/guide") == "example.com/guide"


def test_short_no_path():
    assert _short("https://example.com") == "example.com"


# ── compare_urls ──────────────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_returns_compare_report():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    assert isinstance(cmp, CompareReport)
    assert cmp.url1 == "https://site-a.com/guide"
    assert cmp.url2 == "https://site-b.com/guide"


@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_good_site_leads():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    assert cmp.report1.score > cmp.report2.score
    assert cmp.leader == "url1"
    assert cmp.score_delta < 0  # url2 - url1 is negative when url1 leads


@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_leader_url2():
    _mock_site("https://site-a.com/guide", _HTML_BAD)
    _mock_site("https://site-b.com/guide", _HTML_GOOD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    assert cmp.leader == "url2"
    assert cmp.score_delta > 0


@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_tie():
    _mock_site("https://site-a.com/guide", _HTML_BAD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    assert cmp.leader == "tie"
    assert abs(cmp.score_delta) < 0.5


@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_fetches_both_concurrently():
    """Both requests must be made (no short-circuit)."""
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    assert len(cmp.report1.results) == 16
    assert len(cmp.report2.results) == 16


@respx.mock
@pytest.mark.asyncio
async def test_compare_urls_respects_lang():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide", lang="fr")
    assert cmp.report1.lang == "fr"
    assert cmp.report2.lang == "fr"


# ── render_compare_markdown ───────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_render_compare_markdown_contains_both_urls():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_markdown(cmp)
    assert "site-a.com" in out
    assert "site-b.com" in out


@respx.mock
@pytest.mark.asyncio
async def test_render_compare_markdown_has_categories():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_markdown(cmp)
    assert "STRUCTURE" in out
    assert "HTML" in out
    assert "CONTENT" in out


@respx.mock
@pytest.mark.asyncio
async def test_render_compare_markdown_has_check_names():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_markdown(cmp)
    assert "canonical_url" in out
    assert "single_h1" in out
    assert "word_count" in out


@respx.mock
@pytest.mark.asyncio
async def test_render_compare_markdown_shows_leader():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_markdown(cmp)
    assert "leads" in out


@respx.mock
@pytest.mark.asyncio
async def test_render_compare_markdown_tie():
    _mock_site("https://site-a.com/guide", _HTML_BAD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_markdown(cmp)
    assert "Tied" in out


# ── render_compare_json ───────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_render_compare_json_valid():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    out = render_compare_json(cmp)
    data = json.loads(out)
    assert data["url1"] == "https://site-a.com/guide"
    assert data["url2"] == "https://site-b.com/guide"
    assert "leader" in data
    assert "score_delta" in data
    assert "report1" in data
    assert "report2" in data


@respx.mock
@pytest.mark.asyncio
async def test_render_compare_json_reports_have_results():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    data = json.loads(render_compare_json(cmp))
    assert len(data["report1"]["results"]) == 16
    assert len(data["report2"]["results"]) == 16


# ── CompareReport model ───────────────────────────────────────────────────

@respx.mock
@pytest.mark.asyncio
async def test_compare_report_is_serializable():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    cmp = await compare_urls("https://site-a.com/guide", "https://site-b.com/guide")
    data = cmp.model_dump()
    cmp2 = CompareReport.model_validate(data)
    assert cmp2.url1 == cmp.url1
    assert cmp2.leader == cmp.leader
    assert cmp2.score_delta == cmp.score_delta


# ── CLI integration ───────────────────────────────────────────────────────

@respx.mock
def test_cli_compare_md_output():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    result = CliRunner().invoke(app, ["compare", "https://site-a.com/guide", "https://site-b.com/guide"])
    assert result.exit_code == 0
    assert "site-a.com" in result.output
    assert "site-b.com" in result.output


@respx.mock
def test_cli_compare_json_output():
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    result = CliRunner().invoke(
        app, ["compare", "https://site-a.com/guide", "https://site-b.com/guide", "--format", "json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "url1" in data


@respx.mock
def test_cli_fix_md_output():
    """Smoke test for fix CLI command."""
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    result = CliRunner().invoke(app, ["fix", "https://site-b.com/guide"])
    assert result.exit_code == 0
    assert "Pythia Fix" in result.output


@respx.mock
def test_cli_fix_json_output():
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    result = CliRunner().invoke(app, ["fix", "https://site-b.com/guide", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "fixes" in data
    assert data["fixes_count"] > 0


@respx.mock
def test_cli_fix_output_file(tmp_path):
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    out = tmp_path / "fixes.md"
    result = CliRunner().invoke(app, ["fix", "https://site-b.com/guide", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Pythia Fix" in out.read_text()


@respx.mock
def test_cli_compare_output_file(tmp_path):
    _mock_site("https://site-a.com/guide", _HTML_GOOD)
    _mock_site("https://site-b.com/guide", _HTML_BAD)
    out = tmp_path / "compare.md"
    result = CliRunner().invoke(
        app, ["compare", "https://site-a.com/guide", "https://site-b.com/guide", "--output", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "Pythia Compare" in out.read_text()
