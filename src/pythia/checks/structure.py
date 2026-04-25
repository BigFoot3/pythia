from __future__ import annotations

from urllib.parse import urlparse

from ..fetcher import fetch_url
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


def _base_url(ctx: AuditContext) -> str | None:
    p = urlparse(ctx.url)
    if not p.scheme or not p.netloc:
        return None
    return f"{p.scheme}://{p.netloc}"


def check_robots_blocked(robots_txt: str) -> list[str]:
    """Return sorted list of AI bots blocked by Disallow: / in robots.txt."""
    blocked: set[str] = set()
    current_agents: list[str] = []
    in_rules = False

    for raw_line in robots_txt.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            current_agents = []
            in_rules = False
            continue

        lower = line.lower()
        if lower.startswith("user-agent:"):
            if in_rules:
                current_agents = []
                in_rules = False
            current_agents.append(line[11:].strip())
        elif lower.startswith("disallow:"):
            in_rules = True
            path = line[9:].strip()
            if path == "/":
                for agent in current_agents:
                    if agent == "*":
                        blocked.update(AI_BOTS)
                    elif agent in AI_BOTS:
                        blocked.add(agent)
        elif lower.startswith(("allow:", "crawl-delay:", "sitemap:")):
            in_rules = True

    return sorted(blocked)


class LlmsTxtPresent(BaseCheck):
    name = "llms_txt_present"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        base = _base_url(ctx)
        if not base:
            return self._skip("No base URL — cannot check llms.txt")
        url = f"{base}/llms.txt"
        response = await fetch_url(url, ctx)
        if response and response.status_code == 200 and response.text.strip():
            return self._result("PASS", ctx, details={"url": url, "size": len(response.text)})
        return self._result("FAIL", ctx, details={"url": url},
                            recommendation="Create /llms.txt to help AI systems understand your site. See llmstxt.org")


class LlmsFullTxtPresent(BaseCheck):
    name = "llms_full_txt_present"
    category = "structure"
    weight = 0.5  # bonus check

    async def run(self, ctx: AuditContext) -> CheckResult:
        base = _base_url(ctx)
        if not base:
            return self._skip("No base URL — cannot check llms-full.txt")
        url = f"{base}/llms-full.txt"
        response = await fetch_url(url, ctx)
        if response and response.status_code == 200 and response.text.strip():
            return self._result("PASS", ctx, details={"url": url, "size": len(response.text)})
        return self._result("WARN", ctx, details={"url": url},
                            recommendation="Consider adding /llms-full.txt with complete site content for AI systems")


class RobotsAiBots(BaseCheck):
    name = "robots_ai_bots"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        if not ctx.robots_txt:
            return self._result("WARN", ctx)
        blocked = check_robots_blocked(ctx.robots_txt)
        if blocked:
            return self._result("FAIL", ctx, details={"blocked_bots": blocked},
                                recommendation=f"Remove Disallow: / rules for: {', '.join(blocked)}")
        return self._result("PASS", ctx)


class SitemapAccessible(BaseCheck):
    name = "sitemap_accessible"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        # Check robots.txt for Sitemap: declaration first
        if ctx.robots_txt:
            for line in ctx.robots_txt.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line[8:].strip()
                    resp = await fetch_url(sitemap_url, ctx)
                    if resp and resp.status_code == 200:
                        return self._result("PASS", ctx,
                                            details={"url": sitemap_url, "source": "robots.txt"})

        base = _base_url(ctx)
        if not base:
            return self._skip("No base URL — cannot check sitemap")

        sitemap_url = f"{base}/sitemap.xml"
        resp = await fetch_url(sitemap_url, ctx)
        if resp and resp.status_code == 200:
            return self._result("PASS", ctx, details={"url": sitemap_url, "source": "direct"})

        return self._result("FAIL", ctx,
                            recommendation="Add /sitemap.xml and declare it with Sitemap: in robots.txt")


CHECKS: list[type[BaseCheck]] = [
    LlmsTxtPresent,
    LlmsFullTxtPresent,
    RobotsAiBots,
    SitemapAccessible,
]
