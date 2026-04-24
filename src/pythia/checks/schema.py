from __future__ import annotations

import json

from ..models import AuditContext, CheckResult
from .base import BaseCheck


class JsonLdPresentValid(BaseCheck):
    name = "jsonld_present_valid"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        soup = ctx.get_soup()
        scripts = soup.find_all("script", type="application/ld+json")

        if not scripts:
            return self._result("FAIL", ctx,
                                recommendation="Add JSON-LD structured data — start with @type Organization or Article")

        valid_types: list[str] = []
        invalid_count = 0
        for script in scripts:
            try:
                data = json.loads(script.string or "")
                schema_type = data.get("@type", "unknown") if isinstance(data, dict) else "unknown"
                valid_types.append(schema_type)
            except (ValueError, AttributeError):
                invalid_count += 1

        if valid_types:
            return self._result("PASS", ctx, details={"types": valid_types, "count": len(valid_types)})
        return self._result("WARN", ctx, details={"invalid_count": invalid_count},
                            recommendation="Fix malformed JSON-LD blocks (invalid JSON syntax)")


CHECKS: list[type[BaseCheck]] = [JsonLdPresentValid]
