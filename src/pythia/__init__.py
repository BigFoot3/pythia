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
__version__ = "0.4.0"

from .api import audit_html, audit_url, compare_urls, fix_url
from .fixers import generate_fixes
from .generators import generate_llms_txt
from .models import AuditContext, CheckResult, CompareReport, Fix, FixReport, Report

__all__ = [
    "__version__",
    "audit_url",
    "audit_html",
    "fix_url",
    "compare_urls",
    "generate_fixes",
    "generate_llms_txt",
    "Report",
    "CheckResult",
    "Fix",
    "FixReport",
    "CompareReport",
    "AuditContext",
]
