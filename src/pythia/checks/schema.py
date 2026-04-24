from __future__ import annotations

from ..models import AuditContext, CheckResult
from .base import BaseCheck


class JsonLdPresentValid(BaseCheck):
    name = "jsonld_present_valid"
    category = "structure"
    weight = 1.0

    async def run(self, ctx: AuditContext) -> CheckResult:
        return self._skip("Not implemented yet")


CHECKS: list[type[BaseCheck]] = [JsonLdPresentValid]
