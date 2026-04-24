from __future__ import annotations

from ..models import AuditContext, CheckResult
from .base import BaseCheck

AI_BOTS = [
    "GPTBot",
    "ClaudeBot",
    "PerplexityBot",
    "Google-Extended",
    "CCBot",
    "MistralAI-User",
]


class LlmsTxtPresent(BaseCheck):
    name = "llms_txt_present"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class LlmsFullTxtPresent(BaseCheck):
    name = "llms_full_txt_present"
    category = "structure"
    weight = 0.5  # bonus check

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class RobotsAiBots(BaseCheck):
    name = "robots_ai_bots"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


class SitemapAccessible(BaseCheck):
    name = "sitemap_accessible"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


CHECKS: list[type[BaseCheck]] = [
    LlmsTxtPresent,
    LlmsFullTxtPresent,
    RobotsAiBots,
    SitemapAccessible,
]
