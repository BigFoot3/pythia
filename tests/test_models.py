from pythia.models import AuditContext, CheckResult, Report


def test_check_result_defaults():
    r = CheckResult(name="test", category="html", status="PASS", score=100, message="ok")
    assert r.weight == 1.0
    assert r.details == {}
    assert r.recommendation is None


def test_audit_context_get_soup():
    ctx = AuditContext(url="https://example.com", html="<html><body><h1>Hi</h1></body></html>")
    soup = ctx.get_soup()
    assert soup.find("h1").text == "Hi"


def test_audit_context_soup_cached():
    ctx = AuditContext(url="https://example.com", html="<html><body><h1>Hi</h1></body></html>")
    soup1 = ctx.get_soup()
    soup2 = ctx.get_soup()
    assert soup1 is soup2


def test_audit_context_cache_empty():
    ctx = AuditContext(url="https://example.com")
    assert ctx._cache == {}


def test_report_passed():
    r = Report(
        url="https://example.com",
        score=75.0,
        threshold=70,
        passed=True,
        results=[],
    )
    assert r.passed is True
    assert r.lang == "en"
