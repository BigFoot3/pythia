from __future__ import annotations

from urllib.parse import urlparse

import httpx

from .models import AuditContext

HEADERS = {
    "User-Agent": "pythia-geo/0.2 (+https://github.com/BigFoot3/pythia)",
}
TIMEOUT = 10.0


async def fetch_url(url: str, ctx: AuditContext) -> httpx.Response | None:
    if url in ctx._cache:
        return ctx._cache[url]
    try:
        async with httpx.AsyncClient(
            headers=HEADERS, timeout=TIMEOUT, follow_redirects=True
        ) as client:
            response = await client.get(url)
            ctx._cache[url] = response
            return response
    except Exception:
        ctx._cache[url] = None  # type: ignore[assignment]
        return None


async def fetch_page(ctx: AuditContext) -> str:
    response = await fetch_url(ctx.url, ctx)
    if response and response.status_code == 200:
        return response.text
    return ""


async def fetch_robots(ctx: AuditContext) -> str:
    parsed = urlparse(ctx.url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    response = await fetch_url(robots_url, ctx)
    if response and response.status_code == 200:
        return response.text
    return ""
