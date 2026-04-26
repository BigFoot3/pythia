"""Generate ready-to-paste HTML/server fixes from a Report."""
from __future__ import annotations

from .models import CheckResult, Fix, Report


def generate_fixes(report: Report) -> list[Fix]:
    """Return one Fix for every FAIL/WARN check in *report*."""
    fixes: list[Fix] = []
    for result in report.results:
        if result.status not in ("FAIL", "WARN"):
            continue
        fix = _make_fix(result, report.url)
        if fix is not None:
            fixes.append(fix)
    return fixes


def _make_fix(result: CheckResult, url: str) -> Fix | None:  # noqa: C901
    name = result.name
    status = result.status
    d = result.details

    # ── structure (server-side) ────────────────────────────────────────────
    if name == "llms_txt_present":
        return Fix(
            check_name=name, status=status, location="server",
            snippet="Create /llms.txt at your site root.",
            note="See https://llmstxt.org for the specification.",
        )

    if name == "llms_full_txt_present":
        return Fix(
            check_name=name, status=status, location="server",
            snippet="Create /llms-full.txt with the full text of each page for AI crawlers.",
        )

    if name == "robots_ai_bots":
        blocked = d.get("blocked_bots", [])
        bots = ", ".join(blocked) if blocked else "AI bots"
        return Fix(
            check_name=name, status=status, location="server",
            snippet=f"Remove or restrict 'Disallow: /' for: {bots} in /robots.txt.",
        )

    if name == "sitemap_accessible":
        return Fix(
            check_name=name, status=status, location="server",
            snippet=(
                "1. Create /sitemap.xml\n"
                "2. Declare it in /robots.txt:\n"
                "   Sitemap: https://yourdomain.com/sitemap.xml"
            ),
        )

    # ── <head> ────────────────────────────────────────────────────────────
    if name == "jsonld_present_valid":
        if status == "FAIL":
            snippet = (
                '<script type="application/ld+json">\n'
                "{\n"
                '  "@context": "https://schema.org",\n'
                '  "@type": "WebPage",\n'
                f'  "url": "{url}",\n'
                '  "name": "Your Page Title",\n'
                '  "description": "Your page description."\n'
                "}\n"
                "</script>"
            )
            return Fix(check_name=name, status=status, location="head", snippet=snippet)
        return Fix(
            check_name=name, status=status, location="head",
            snippet="<!-- Fix JSON syntax in your existing <script type='application/ld+json'> block -->",
            note="Validate at https://validator.schema.org/",
        )

    if name == "title_length":
        if status == "FAIL":
            return Fix(
                check_name=name, status=status, location="head",
                snippet="<title>Your descriptive page title (30–65 chars)</title>",
            )
        length = d.get("length", 0)
        direction = "Expand" if length < 30 else "Shorten"
        return Fix(
            check_name=name, status=status, location="head",
            snippet=f"<!-- {direction} your <title> to 30–65 characters -->",
            note=f"Current length: {length} chars",
        )

    if name == "meta_description":
        if status == "FAIL":
            desc = "A compelling page description between 70 and 160 characters."
            return Fix(
                check_name=name, status=status, location="head",
                snippet=f'<meta name="description" content="{desc}">',
            )
        length = d.get("length", 0)
        direction = "Expand" if length < 70 else "Shorten"
        return Fix(
            check_name=name, status=status, location="head",
            snippet=f"<!-- {direction} your meta description to 70–160 characters -->",
            note=f"Current length: {length} chars",
        )

    if name == "opengraph_minimal":
        missing = d.get("missing", ["og:title", "og:description", "og:type"])
        lines = []
        if "og:title" in missing:
            lines.append('<meta property="og:title" content="Your Page Title">')
        if "og:description" in missing:
            lines.append('<meta property="og:description" content="Your page description.">')
        if "og:type" in missing:
            lines.append('<meta property="og:type" content="website">')
        return Fix(check_name=name, status=status, location="head", snippet="\n".join(lines))

    if name == "canonical_url":
        return Fix(
            check_name=name, status=status, location="head",
            snippet=f'<link rel="canonical" href="{url}">',
        )

    # ── <body> ────────────────────────────────────────────────────────────
    if name == "single_h1":
        if status == "FAIL":
            return Fix(
                check_name=name, status=status, location="body",
                snippet="<h1>Your Main Page Heading</h1>",
                note="Place exactly one H1 at the top of your main content area.",
            )
        count = d.get("h1_count", 2)
        return Fix(
            check_name=name, status=status, location="body",
            snippet=f"<!-- Remove {count - 1} extra <h1> tag(s) — keep only one -->",
        )

    if name == "heading_hierarchy":
        gaps = d.get("gaps", [])
        if not gaps:
            return None
        from_lvl, to_lvl = gaps[0]
        return Fix(
            check_name=name, status=status, location="body",
            snippet=(
                f"<!-- Fix heading level gap: H{from_lvl} → H{to_lvl}\n"
                f"     Insert H{from_lvl + 1} between them -->"
            ),
            note="Sequential heading levels help AI parse your content hierarchy.",
        )

    if name == "generic_headings":
        generics = d.get("generic_headings", [])
        examples = ", ".join(f'<{g["tag"]}>{g["text"]}</{g["tag"]}>' for g in generics[:3])
        return Fix(
            check_name=name, status=status, location="body",
            snippet=f"<!-- Replace generic headings with descriptive titles: {examples} -->",
        )

    if name == "faq_pattern":
        snippet = (
            "<dl>\n"
            "  <dt>Question one?</dt>\n"
            "  <dd>Answer to question one.</dd>\n"
            "  <dt>Question two?</dt>\n"
            "  <dd>Answer to question two.</dd>\n"
            "</dl>"
        )
        return Fix(
            check_name=name, status=status, location="body", snippet=snippet,
            note="Alternatively use <details><summary>…</summary></details> for accordion style.",
        )

    if name == "eeat_signals":
        has_author = d.get("has_author", False)
        has_date = d.get("has_date", False)
        lines = []
        if not has_author:
            lines += [
                '<span itemprop="author" itemscope itemtype="https://schema.org/Person">',
                '  <span itemprop="name">Author Name</span>',
                "</span>",
            ]
        if not has_date:
            lines.append('<time itemprop="datePublished" datetime="YYYY-MM-DD">Month Day, Year</time>')
        return Fix(check_name=name, status=status, location="body", snippet="\n".join(lines))

    if name == "structured_content":
        snippet = (
            "<ul>\n"
            "  <li>First item</li>\n"
            "  <li>Second item</li>\n"
            "  <li>Third item</li>\n"
            "</ul>"
        )
        return Fix(
            check_name=name, status=status, location="body", snippet=snippet,
            note="Or use <ol> for ordered content, <table> for tabular data.",
        )

    # ── content (no single HTML snippet — guidance only) ──────────────────
    if name == "word_count":
        count = d.get("word_count", 0)
        min_rec = d.get("min_recommended", 300)
        needed = max(0, min_rec - count)
        return Fix(
            check_name=name, status=status, location="content",
            snippet=f"<!-- Add ~{needed} more words of substantive content -->",
            note=f"Current: {count} words. Target: ≥ {min_rec} words.",
        )

    return None
