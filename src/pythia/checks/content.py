from __future__ import annotations

from ..models import AuditContext, CheckResult
from .base import BaseCheck


class GenericHeadings(BaseCheck):
    name = "generic_headings"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class FaqPattern(BaseCheck):
    name = "faq_pattern"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class EeatSignals(BaseCheck):
    name = "eeat_signals"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class StructuredContent(BaseCheck):
    name = "structured_content"
    category = "content"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


CHECKS: list[type[BaseCheck]] = [
    GenericHeadings,
    FaqPattern,
    EeatSignals,
    StructuredContent,
]
