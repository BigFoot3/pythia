from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, PrivateAttr

PageType = Literal["auto", "article", "homepage", "doc"]
ResolvedPageType = Literal["article", "homepage", "doc"]

_HOMEPAGE_PATHS = {"", "/", "/index.html", "/index.php", "/index.htm"}


class AuditContext(BaseModel):
    url: str
    lang: Literal["fr", "en"] = "en"
    html: str = ""
    robots_txt: str = ""
    page_type: PageType = "auto"

    model_config = {"arbitrary_types_allowed": True}

    _soup: BeautifulSoup | None = PrivateAttr(default=None)
    _cache: dict[str, Any] = PrivateAttr(default_factory=dict)

    def get_soup(self) -> BeautifulSoup:
        if self._soup is None:
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup

    def effective_page_type(self) -> ResolvedPageType:
        if self.page_type != "auto":
            return self.page_type  # type: ignore[return-value]
        path = urlparse(self.url).path.rstrip("/")
        return "homepage" if path in _HOMEPAGE_PATHS else "article"


class CheckResult(BaseModel):
    name: str
    category: Literal["structure", "html", "content"]
    status: Literal["PASS", "WARN", "FAIL", "SKIP"]
    score: int  # PASS=100, WARN=50, FAIL=0, SKIP=0 (excluded from calc)
    weight: float = 1.0
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    recommendation: str | None = None


class Report(BaseModel):
    url: str
    lang: Literal["fr", "en"] = "en"
    page_type: ResolvedPageType = "article"
    score: float
    threshold: int
    passed: bool
    results: list[CheckResult]
    scores_by_category: dict[str, float] = Field(default_factory=dict)
