"""Tests for pythia generate-llms (generate_llms_txt)."""
import httpx
import pytest
import respx

from pythia import generate_llms_txt
from pythia.generators.llms_txt import _PageInfo, _parse_sitemap, _render, _section_for_path

# ── test fixtures ──────────────────────────────────────────────────────────

_SITEMAP_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/blog/post-1</loc></url>
  <url><loc>https://example.com/blog/post-2</loc></url>
  <url><loc>https://example.com/docs/api</loc></url>
</urlset>"""

_SITEMAP_INDEX_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/sitemap-pages.xml</loc></sitemap>
  <sitemap><loc>https://example.com/sitemap-blog.xml</loc></sitemap>
</sitemapindex>"""

_SITEMAP_CHILD_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/page-a</loc></url>
  <url><loc>https://example.com/page-b</loc></url>
</urlset>"""

_HOMEPAGE_HTML = """\
<html><head>
  <title>Example Site</title>
  <meta name="description" content="The best example site on the internet.">
</head><body><h1>Welcome</h1></body></html>"""

_ARTICLE_HTML = """\
<html><head>
  <title>Blog Post 1 | Example Site</title>
  <meta name="description" content="First blog post.">
</head><body><h1>Blog Post 1</h1></body></html>"""

_DOCS_HTML = """\
<html><head>
  <title>API Reference | Example Site</title>
  <meta property="og:description" content="Complete API docs.">
</head><body></body></html>"""


# ── pure function tests ────────────────────────────────────────────────────

def test_parse_sitemap_regular():
    urls, is_index = _parse_sitemap(_SITEMAP_XML, 100)
    assert is_index is False
    assert len(urls) == 5
    assert "https://example.com/about" in urls


def test_parse_sitemap_index():
    urls, is_index = _parse_sitemap(_SITEMAP_INDEX_XML, 100)
    assert is_index is True
    assert len(urls) == 2
    assert "https://example.com/sitemap-pages.xml" in urls


def test_parse_sitemap_respects_max_pages():
    urls, _ = _parse_sitemap(_SITEMAP_XML, 2)
    assert len(urls) == 2


def test_parse_sitemap_invalid_xml():
    urls, is_index = _parse_sitemap("not xml at all <<<", 100)
    assert urls == []
    assert is_index is False


def test_parse_sitemap_empty():
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
    urls, _ = _parse_sitemap(xml, 100)
    assert urls == []


@pytest.mark.parametrize("path,expected", [
    ("", "Main"),
    ("/", "Main"),
    ("/about", "About"),
    ("/blog/post-1", "Blog"),
    ("/docs/api/reference", "Docs"),
    ("/my-projects", "My Projects"),
    ("/api_docs", "Api Docs"),
])
def test_section_for_path(path, expected):
    assert _section_for_path(path) == expected


def test_render_basic():
    pages = [
        _PageInfo(url="https://example.com/about", title="About Us",
                  description="Who we are.", section="About"),
        _PageInfo(url="https://example.com/blog/post", title="A Post",
                  description="Post content.", section="Blog"),
    ]
    result = _render("Example", "Great site.", pages)
    assert "# Example" in result
    assert "> Great site." in result
    assert "## About" in result
    assert "## Blog" in result
    assert "[About Us](https://example.com/about): Who we are." in result
    assert "[A Post](https://example.com/blog/post): Post content." in result


def test_render_main_section_first():
    pages = [
        _PageInfo(url="https://example.com/z", title="Z Page", section="Zzz"),
        _PageInfo(url="https://example.com/", title="Home", section="Main"),
    ]
    result = _render("Site", "", pages)
    main_pos = result.index("## Main")
    z_pos = result.index("## Zzz")
    assert main_pos < z_pos


def test_render_no_description():
    pages = [_PageInfo(url="https://example.com/a", title="A", section="Main")]
    result = _render("Site", "", pages)
    assert ">" not in result  # no blockquote


def test_render_page_without_description():
    pages = [_PageInfo(url="https://example.com/a", title="A Page", section="Main")]
    result = _render("Site", "Desc.", pages)
    assert "[A Page](https://example.com/a)\n" in result or "[A Page](https://example.com/a)" in result
    assert ": " not in result.split("## Main")[1]


def test_render_fallback_url_as_title():
    pages = [_PageInfo(url="https://example.com/no-title", title="", section="Pages")]
    result = _render("Site", "", pages)
    assert "[https://example.com/no-title]" in result


# ── integration tests (respx) ──────────────────────────────────────────────

def _mock_site(base: str = "https://example.com") -> None:
    """Register respx mocks for a minimal site."""
    respx.get(f"{base}/robots.txt").mock(return_value=httpx.Response(404))
    respx.get(f"{base}/sitemap.xml").mock(
        return_value=httpx.Response(200, text=_SITEMAP_XML)
    )
    respx.get(f"{base}/").mock(return_value=httpx.Response(200, text=_HOMEPAGE_HTML))
    respx.get(f"{base}/about").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get(f"{base}/blog/post-1").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get(f"{base}/blog/post-2").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get(f"{base}/docs/api").mock(return_value=httpx.Response(200, text=_DOCS_HTML))


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_returns_string():
    _mock_site()
    result = await generate_llms_txt("https://example.com")
    assert isinstance(result, str)
    assert len(result) > 0


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_has_title():
    _mock_site()
    result = await generate_llms_txt("https://example.com")
    assert "# Example Site" in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_has_description():
    _mock_site()
    result = await generate_llms_txt("https://example.com")
    assert "> The best example site on the internet." in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_has_sections():
    _mock_site()
    result = await generate_llms_txt("https://example.com")
    assert "## Blog" in result
    assert "## Docs" in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_has_links():
    _mock_site()
    result = await generate_llms_txt("https://example.com")
    assert "https://example.com/blog/post-1" in result
    assert "https://example.com/docs/api" in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_respects_max_pages():
    _mock_site()
    result = await generate_llms_txt("https://example.com", max_pages=2)
    # Only 2 pages from sitemap should be present
    link_count = result.count("](https://example.com/")
    assert link_count <= 2


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_no_sitemap_fallback_to_homepage():
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/").mock(return_value=httpx.Response(200, text=_HOMEPAGE_HTML))
    result = await generate_llms_txt("https://example.com")
    assert "# Example Site" in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_sitemap_via_robots_txt():
    respx.get("https://example.com/robots.txt").mock(
        return_value=httpx.Response(200, text="Sitemap: https://example.com/sitemap.xml\n")
    )
    respx.get("https://example.com/sitemap.xml").mock(
        return_value=httpx.Response(200, text=_SITEMAP_XML)
    )
    respx.get("https://example.com/").mock(return_value=httpx.Response(200, text=_HOMEPAGE_HTML))
    respx.get("https://example.com/about").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/blog/post-1").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/blog/post-2").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/docs/api").mock(return_value=httpx.Response(200, text=_DOCS_HTML))
    result = await generate_llms_txt("https://example.com")
    assert "# Example Site" in result


@respx.mock
@pytest.mark.asyncio
async def test_generate_llms_txt_sitemap_index():
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(
        return_value=httpx.Response(200, text=_SITEMAP_INDEX_XML)
    )
    respx.get("https://example.com/sitemap-pages.xml").mock(
        return_value=httpx.Response(200, text=_SITEMAP_CHILD_XML)
    )
    respx.get("https://example.com/").mock(return_value=httpx.Response(200, text=_HOMEPAGE_HTML))
    respx.get("https://example.com/page-a").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    respx.get("https://example.com/page-b").mock(return_value=httpx.Response(200, text=_ARTICLE_HTML))
    result = await generate_llms_txt("https://example.com")
    assert "https://example.com/page-a" in result


@pytest.mark.asyncio
async def test_generate_llms_txt_invalid_url():
    with pytest.raises(ValueError, match="Invalid URL"):
        await generate_llms_txt("not-a-url")


# ── public API export ──────────────────────────────────────────────────────

def test_generate_llms_txt_exported():
    import pythia
    assert hasattr(pythia, "generate_llms_txt")
    assert callable(pythia.generate_llms_txt)
