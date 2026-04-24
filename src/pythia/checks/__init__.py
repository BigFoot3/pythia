from .base import BaseCheck
from .content import CHECKS as CONTENT_CHECKS
from .html import CHECKS as HTML_CHECKS
from .schema import CHECKS as SCHEMA_CHECKS
from .structure import CHECKS as STRUCTURE_CHECKS

ALL_CHECKS: list[type[BaseCheck]] = (
    STRUCTURE_CHECKS + SCHEMA_CHECKS + HTML_CHECKS + CONTENT_CHECKS
)

__all__ = ["ALL_CHECKS", "BaseCheck"]
