"""Public async API — usable as a library without the CLI."""
from __future__ import annotations

from .checks import ALL_CHECKS
from .fetcher import fetch_page, fetch_robots
from .models import AuditContext, CheckResult, Report
from .scoring import build_report


async def _run_checks(ctx: AuditContext) -> list[CheckResult]:
    results = []
    for check_cls in ALL_CHECKS:
        results.append(await check_cls().run(ctx))
    return results


async def audit_url(
    url: str,
    lang: str = "en",
    page_type: str = "auto",
    threshold: int = 70,
) -> Report:
    """Fetch *url* over HTTP and return a full GEO/AEO audit report.

    Example::

        import asyncio
        from pythia import audit_url

        report = asyncio.run(audit_url("https://example.com"))
        print(report.score, report.passed)
    """
    ctx = AuditContext(url=url, lang=lang, page_type=page_type)  # type: ignore[arg-type]
    ctx.html = await fetch_page(ctx)
    ctx.robots_txt = await fetch_robots(ctx)
    ctx.get_soup()
    results = await _run_checks(ctx)
    return build_report(url, results, threshold=threshold, lang=lang,
                        page_type=ctx.effective_page_type())


async def audit_html(
    html: str,
    base_url: str = "",
    lang: str = "en",
    page_type: str = "auto",
    threshold: int = 70,
) -> Report:
    """Audit raw HTML directly — no HTTP fetch for the page itself.

    Structure checks that require network access (``llms_txt``, ``sitemap``,
    ``robots_ai_bots``) will SKIP when *base_url* is empty or has no scheme.
    Provide *base_url* to enable those checks.

    Example::

        import asyncio
        from pythia import audit_html

        with open("index.html") as f:
            report = asyncio.run(audit_html(f.read(), base_url="https://example.com"))
    """
    ctx = AuditContext(url=base_url, html=html, lang=lang, page_type=page_type)  # type: ignore[arg-type]
    ctx.get_soup()
    results = await _run_checks(ctx)
    label = base_url or "<html>"
    return build_report(label, results, threshold=threshold, lang=lang,
                        page_type=ctx.effective_page_type())
