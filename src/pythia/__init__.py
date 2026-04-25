"""pythia-geo — GEO/AEO audit library and CLI.

Quick start::

    import asyncio
    from pythia import audit_url, audit_html

    # Audit a live URL
    report = asyncio.run(audit_url("https://example.com"))
    print(f"Score: {report.score}/100  passed={report.passed}")

    # Audit raw HTML (offline / CI)
    report = asyncio.run(audit_html("<html>...</html>", base_url="https://example.com"))
"""
__version__ = "0.2.1"

from .api import audit_html, audit_url
from .models import AuditContext, CheckResult, Report

__all__ = [
    "__version__",
    "audit_url",
    "audit_html",
    "Report",
    "CheckResult",
    "AuditContext",
]
