"""Generate a valid llms.txt file by crawling a site's sitemap."""
from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ..fetcher import HEADERS, TIMEOUT

# Max pages to crawl when the sitemap has no limit declared
_HARD_CAP = 500


@dataclass
class _PageInfo:
    url: str
    title: str = ""
    description: str = ""
    section: str = "Pages"


# ── sitemap helpers ────────────────────────────────────────────────────────

def _strip_ns(tag: str) -> str:
    """Remove XML namespace prefix from a tag name."""
    return tag.split("}", 1)[1] if "}" in tag else tag


def _parse_sitemap(xml_text: str, max_pages: int) -> tuple[list[str], bool]:
    """Return (urls, is_index).

    *is_index* is True when the XML is a sitemapindex pointing to child sitemaps.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return [], False

    root_tag = _strip_ns(root.tag)

    if root_tag == "sitemapindex":
        urls = [
            loc.text.strip()
            for sm in root
            if _strip_ns(sm.tag) == "sitemap"
            for loc in sm
            if _strip_ns(loc.tag) == "loc" and loc.text
        ]
        return urls[:max_pages], True

    # Regular urlset
    urls = [
        loc.text.strip()
        for url_elem in root
        if _strip_ns(url_elem.tag) == "url"
        for loc in url_elem
        if _strip_ns(loc.tag) == "loc" and loc.text
    ]
    return urls[:max_pages], False


async def _find_sitemap_url(client: httpx.AsyncClient, base_url: str) -> str | None:
    """Return the sitemap URL declared in robots.txt, or None."""
    try:
        r = await client.get(f"{base_url}/robots.txt")
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    return line[8:].strip()
    except Exception:
        pass
    return None


async def _resolve_urls(
    client: httpx.AsyncClient, base_url: str, max_pages: int
) -> list[str]:
    """Return a list of page URLs from the site's sitemap (up to max_pages)."""
    sitemap_url = await _find_sitemap_url(client, base_url) or f"{base_url}/sitemap.xml"

    try:
        r = await client.get(sitemap_url)
        if r.status_code != 200:
            return []
    except Exception:
        return []

    urls, is_index = _parse_sitemap(r.text, max_pages)

    if is_index and urls:
        # Fetch the first child sitemap to get actual page URLs
        try:
            r2 = await client.get(urls[0])
            if r2.status_code == 200:
                page_urls, _ = _parse_sitemap(r2.text, max_pages)
                return page_urls
        except Exception:
            pass
        return []

    return urls


# ── page info fetching ─────────────────────────────────────────────────────

def _section_for_path(path: str) -> str:
    """Map a URL path to a section name."""
    clean = path.strip("/")
    if not clean:
        return "Main"
    first = clean.split("/")[0]
    return first.replace("-", " ").replace("_", " ").title()


async def _fetch_page_info(client: httpx.AsyncClient, url: str) -> _PageInfo:
    path = urlparse(url).path
    info = _PageInfo(url=url, section=_section_for_path(path))
    try:
        r = await client.get(url)
        if r.status_code != 200:
            return info
        soup = BeautifulSoup(r.text, "lxml")

        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            info.title = title_tag.string.strip()

        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            info.description = str(meta["content"]).strip()
        if not info.description:
            og = soup.find("meta", property="og:description")
            if og and og.get("content"):
                info.description = str(og["content"]).strip()
    except Exception:
        pass
    return info


# ── renderer ──────────────────────────────────────────────────────────────

def _render(site_name: str, site_description: str, pages: list[_PageInfo]) -> str:
    lines: list[str] = [f"# {site_name}", ""]
    if site_description:
        lines += [f"> {site_description}", ""]

    # Group by section, Main first then alphabetical
    sections: dict[str, list[_PageInfo]] = {}
    for page in pages:
        sections.setdefault(page.section, []).append(page)

    ordered = sorted(sections.keys(), key=lambda s: (s != "Main", s.lower()))

    for section in ordered:
        lines += [f"## {section}", ""]
        for page in sections[section]:
            title = page.title or page.url
            desc = f": {page.description}" if page.description else ""
            lines.append(f"- [{title}]({page.url}){desc}")
        lines.append("")

    return "\n".join(lines)


# ── public entry point ────────────────────────────────────────────────────

async def generate_llms_txt(
    url: str,
    max_pages: int = 50,
    concurrency: int = 5,
) -> str:
    """Crawl *url*'s sitemap and return a ready-to-deploy ``llms.txt`` string.

    Steps:
    1. Reads ``robots.txt`` to find a ``Sitemap:`` declaration (falls back to ``/sitemap.xml``).
    2. Parses the sitemap XML; follows one level of sitemap index.
    3. Fetches up to *max_pages* pages concurrently (bounded by *concurrency*).
    4. Groups pages by their first URL path segment into sections.
    5. Returns the ``llms.txt`` Markdown string.

    Example::

        import asyncio
        from pythia import generate_llms_txt

        content = asyncio.run(generate_llms_txt("https://example.com"))
        with open("llms.txt", "w") as f:
            f.write(content)
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url!r} — must include scheme and host")

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    async with httpx.AsyncClient(
        headers=HEADERS, timeout=TIMEOUT, follow_redirects=True
    ) as client:
        # Resolve sitemap → page URL list
        page_urls = await _resolve_urls(client, base_url, min(max_pages, _HARD_CAP))

        # Fetch homepage info for H1 + blockquote
        homepage = await _fetch_page_info(client, base_url)

        # Fetch page infos concurrently
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded(u: str) -> _PageInfo:
            async with semaphore:
                return await _fetch_page_info(client, u)

        if page_urls:
            results = await asyncio.gather(*[bounded(u) for u in page_urls])
            pages = list(results)
        else:
            pages = [homepage]

    site_name = homepage.title or parsed.netloc
    site_description = homepage.description

    return _render(site_name, site_description, pages)
