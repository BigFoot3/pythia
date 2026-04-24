from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ..models import AuditContext

from ..i18n import get_message
from ..models import CheckResult

_SCORE_MAP = {"PASS": 100, "WARN": 50, "FAIL": 0}


class BaseCheck(ABC):
    name: str
    category: Literal["structure", "html", "content"]
    weight: float = 1.0

    @abstractmethod
    async def run(self, ctx: AuditContext) -> CheckResult: ...

    def _result(
        self,
        status: Literal["PASS", "WARN", "FAIL"],
        ctx: AuditContext,
        details: dict[str, Any] | None = None,
        recommendation: str | None = None,
    ) -> CheckResult:
        return CheckResult(
            name=self.name,
            category=self.category,
            status=status,
            score=_SCORE_MAP[status],
            weight=self.weight,
            message=get_message(self.name, status, ctx.lang),
            details=details or {},
            recommendation=recommendation,
        )

    def _skip(self, reason: str = "") -> CheckResult:
        return CheckResult(
            name=self.name,
            category=self.category,
            status="SKIP",
            score=0,
            weight=self.weight,
            message=reason or f"Check {self.name} skipped",
            details={},
        )
