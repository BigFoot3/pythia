from __future__ import annotations

import copy
import json
import re

from ..models import AuditContext, CheckResult
from .base import BaseCheck

_GENERIC_WORDS = {"home", "welcome", "page", "untitled"}
_AUTHOR_CLS = re.compile(r"\bauthor\b", re.I)
_BYLINE_CLS = re.compile(r"\bbyline\b", re.I)
_NOISE_TAGS = {"script", "style", "nav", "header", "footer", "aside"}


class GenericHeadings(BaseCheck):
    name = "generic_headings"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        soup = ctx.get_soup()
        generic = [
            {"tag": h.name, "text": h.get_text(strip=True)}
            for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if h.get_text(strip=True).lower() in _GENERIC_WORDS
        ]
        if not generic:
            return self._result("PASS", ctx)
        h1_generic = any(g["tag"] == "h1" for g in generic)
        if h1_generic or len(generic) >= 3:
            return self._result("FAIL", ctx, details={"generic_headings": generic},
                                recommendation="Replace generic headings with descriptive titles")
        return self._result("WARN", ctx, details={"generic_headings": generic},
                            recommendation="Replace generic headings with descriptive titles")


class FaqPattern(BaseCheck):
    name = "faq_pattern"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        if ctx.effective_page_type() == "homepage":
            return self._skip("FAQ pattern not evaluated for homepage")

        soup = ctx.get_soup()

        # Schema.org FAQPage via microdata
        if soup.find(attrs={"itemtype": re.compile(r"FAQPage", re.I)}):
            return self._result("PASS", ctx, details={"method": "microdata_faqpage"})

        # FAQPage in JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and "FAQPage" in str(data.get("@type", "")):
                    return self._result("PASS", ctx, details={"method": "jsonld_faqpage"})
            except (ValueError, AttributeError):
                pass

        # <dl> definition list
        if soup.find("dl"):
            return self._result("PASS", ctx, details={"method": "dl_element"})

        # <details><summary> accordion pattern
        if soup.find("details") and soup.find("summary"):
            return self._result("PASS", ctx, details={"method": "details_summary"})

        return self._result("WARN", ctx,
                            recommendation="Add a FAQ section using <dl>, <details><summary>, or FAQPage JSON-LD")


class EeatSignals(BaseCheck):
    name = "eeat_signals"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        if ctx.effective_page_type() == "homepage":
            return self._skip("E-E-A-T signals not evaluated for homepage")

        soup = ctx.get_soup()

        has_author = bool(
            soup.find(rel="author")
            or soup.find(itemprop="author")
            or soup.find(class_=_AUTHOR_CLS)
            or soup.find(class_=_BYLINE_CLS)
        )
        has_date = bool(
            soup.find("time")
            or soup.find(itemprop="datePublished")
            or soup.find("meta", property="article:published_time")
        )

        details = {"has_author": has_author, "has_date": has_date}
        if has_author and has_date:
            return self._result("PASS", ctx, details=details)
        if has_author or has_date:
            missing = "publication date" if has_author else "author name"
            return self._result("WARN", ctx, details=details,
                                recommendation=f"Add {missing} for stronger E-E-A-T signals")
        return self._result("FAIL", ctx, details=details,
                            recommendation="Add author name and publication date for E-E-A-T signals")


class StructuredContent(BaseCheck):
    name = "structured_content"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        body = ctx.get_soup().find("body") or ctx.get_soup()
        has_ul = bool(body.find("ul"))
        has_ol = bool(body.find("ol"))
        has_table = bool(body.find("table"))
        details = {"has_ul": has_ul, "has_ol": has_ol, "has_table": has_table}
        if has_ul or has_ol or has_table:
            return self._result("PASS", ctx, details=details)
        return self._result("FAIL", ctx, details=details,
                            recommendation="Add structured content using <ul>, <ol>, or <table> elements")


class WordCount(BaseCheck):
    name = "word_count"
    category = "content"
    weight = 1.0

    MIN_PASS = 300
    MIN_WARN = 100

    async def run(self, ctx: AuditContext) -> CheckResult:
        if ctx.effective_page_type() == "homepage":
            return self._skip("Word count not evaluated for homepage")

        soup = ctx.get_soup()
        body = copy.deepcopy(soup.find("body") or soup)
        for tag in body.find_all(list(_NOISE_TAGS)):
            tag.decompose()
        text = body.get_text(separator=" ", strip=True)
        count = len(text.split())

        details = {"word_count": count, "min_recommended": self.MIN_PASS}
        if count >= self.MIN_PASS:
            return self._result("PASS", ctx, details=details)
        if count >= self.MIN_WARN:
            return self._result("WARN", ctx, details=details,
                                recommendation=f"Add more content — {count} words found, aim for ≥ {self.MIN_PASS}")
        return self._result("FAIL", ctx, details=details,
                            recommendation=f"Content too short — {count} words found, aim for ≥ {self.MIN_PASS}")


CHECKS: list[type[BaseCheck]] = [
    GenericHeadings,
    FaqPattern,
    EeatSignals,
    StructuredContent,
    WordCount,
]
