from __future__ import annotations

from ..models import AuditContext, CheckResult
from .base import BaseCheck


class SingleH1(BaseCheck):
    name = "single_h1"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class HeadingHierarchy(BaseCheck):
    name = "heading_hierarchy"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class TitleLength(BaseCheck):
    name = "title_length"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class MetaDescription(BaseCheck):
    name = "meta_description"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class OpenGraphMinimal(BaseCheck):
    name = "opengraph_minimal"
    category = "html"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


CHECKS: list[type[BaseCheck]] = [
    SingleH1,
    HeadingHierarchy,
    TitleLength,
    MetaDescription,
    OpenGraphMinimal,
]
