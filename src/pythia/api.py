"""Public async API — usable as a library without the CLI."""
from __future__ import annotations

import asyncio

from .checks import ALL_CHECKS
from .fetcher import fetch_page, fetch_robots
from .fixers import generate_fixes
from .models import AuditContext, CheckResult, CompareReport, FixReport, Report
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


async def fix_url(
    url: str,
    lang: str = "en",
    page_type: str = "auto",
    threshold: int = 70,
) -> FixReport:
    """Audit *url* and return a :class:`FixReport` with ready-to-paste HTML snippets.

    Example::

        import asyncio
        from pythia import fix_url

        fix_report = asyncio.run(fix_url("https://example.com"))
        for fix in fix_report.fixes:
            print(fix.check_name, fix.location)
            print(fix.snippet)
    """
    report = await audit_url(url, lang=lang, page_type=page_type, threshold=threshold)
    fixes = generate_fixes(report)
    return FixReport(url=url, audit=report, fixes=fixes)


async def compare_urls(
    url1: str,
    url2: str,
    lang: str = "en",
    threshold: int = 70,
) -> CompareReport:
    """Audit *url1* and *url2* concurrently and return a :class:`CompareReport`.

    Example::

        import asyncio
        from pythia import compare_urls

        cmp = asyncio.run(compare_urls("https://site-a.com", "https://site-b.com"))
        print(f"{cmp.url1} {cmp.report1.score:.0f}  vs  {cmp.url2} {cmp.report2.score:.0f}")
        print("leader:", cmp.leader)
    """
    report1, report2 = await asyncio.gather(
        audit_url(url1, lang=lang, threshold=threshold),
        audit_url(url2, lang=lang, threshold=threshold),
    )
    delta = round(report2.score - report1.score, 1)
    if abs(delta) < 0.5:
        leader = "tie"
    elif delta < 0:
        leader = "url1"
    else:
        leader = "url2"
    return CompareReport(
        url1=url1, url2=url2,
        report1=report1, report2=report2,
        score_delta=delta, leader=leader,  # type: ignore[arg-type]
    )
