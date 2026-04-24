from __future__ import annotations

from ..models import AuditContext, CheckResult
from .base import BaseCheck

_REQUIRED_OG = ["og:title", "og:description", "og:type"]


class SingleH1(BaseCheck):
    name = "single_h1"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        h1s = ctx.get_soup().find_all("h1")
        count = len(h1s)
        if count == 0:
            return self._result("FAIL", ctx, details={"h1_count": 0},
                                recommendation="Add exactly one <h1> heading per page")
        if count > 1:
            return self._result("WARN", ctx, details={"h1_count": count},
                                recommendation=f"Reduce to one <h1> (found {count})")
        return self._result("PASS", ctx, details={"h1_count": 1})


class HeadingHierarchy(BaseCheck):
    name = "heading_hierarchy"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        headings = ctx.get_soup().find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        levels = [int(h.name[1]) for h in headings]
        gaps = [
            (levels[i - 1], levels[i])
            for i in range(1, len(levels))
            if levels[i] > levels[i - 1] + 1
        ]
        if gaps:
            example = f"H{gaps[0][0]} → H{gaps[0][1]}"
            return self._result("FAIL", ctx, details={"gaps": gaps},
                                recommendation=f"Fix heading hierarchy — example gap: {example}")
        return self._result("PASS", ctx, details={"levels": levels})


class TitleLength(BaseCheck):
    name = "title_length"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        tag = ctx.get_soup().find("title")
        if not tag or not tag.string:
            return self._result("FAIL", ctx,
                                recommendation="Add a <title> tag (30–65 characters)")
        title = tag.string.strip()
        length = len(title)
        if 30 <= length <= 65:
            return self._result("PASS", ctx, details={"length": length})
        direction = "too short" if length < 30 else "too long"
        return self._result("WARN", ctx, details={"length": length},
                            recommendation=f"Title is {length} chars ({direction}) — aim for 30–65")


class MetaDescription(BaseCheck):
    name = "meta_description"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        meta = ctx.get_soup().find("meta", attrs={"name": "description"})
        if not meta or not meta.get("content"):
            return self._result("FAIL", ctx,
                                recommendation="Add <meta name=\"description\" content=\"...\"> (70–160 characters)")
        content = str(meta["content"]).strip()
        length = len(content)
        if 70 <= length <= 160:
            return self._result("PASS", ctx, details={"length": length})
        direction = "too short" if length < 70 else "too long"
        return self._result("WARN", ctx, details={"length": length},
                            recommendation=f"Meta description is {length} chars ({direction}) — aim for 70–160")


class OpenGraphMinimal(BaseCheck):
    name = "opengraph_minimal"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        soup = ctx.get_soup()
        present = [t for t in _REQUIRED_OG if soup.find("meta", property=t)]
        missing = [t for t in _REQUIRED_OG if t not in present]

        if len(present) == 3:
            return self._result("PASS", ctx, details={"found": present})
        if not present:
            return self._result("FAIL", ctx, details={"missing": missing},
                                recommendation="Add og:title, og:description, og:type <meta property> tags")
        return self._result("WARN", ctx, details={"found": present, "missing": missing},
                            recommendation=f"Add missing OpenGraph tags: {', '.join(missing)}")


CHECKS: list[type[BaseCheck]] = [
    SingleH1,
    HeadingHierarchy,
    TitleLength,
    MetaDescription,
    OpenGraphMinimal,
]
