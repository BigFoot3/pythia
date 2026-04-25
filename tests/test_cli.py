import httpx
import respx
from typer.testing import CliRunner

from pythia.cli import app

runner = CliRunner()

_STUB_HTML = """\
<!DOCTYPE html><html><head><title>Test</title></head>
<body><h1>Hello</h1></body></html>"""


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "pythia-geo" in result.output
    assert "0.1.0" in result.output


def test_list_checks():
    result = runner.invoke(app, ["list-checks"])
    assert result.exit_code == 0
    assert "llms_txt_present" in result.output
    assert "single_h1" in result.output
    assert "faq_pattern" in result.output


def test_list_checks_has_16_rows():
    result = runner.invoke(app, ["list-checks"])
    assert result.exit_code == 0
    # 16 checks defined (14 original + canonical_url + word_count)
    count = sum(
        1 for line in result.output.splitlines()
        if any(name in line for name in [
            "llms_txt_present", "llms_full_txt_present", "robots_ai_bots",
            "sitemap_accessible", "jsonld_present_valid", "single_h1",
            "heading_hierarchy", "title_length", "meta_description",
            "opengraph_minimal", "canonical_url", "generic_headings",
            "faq_pattern", "eeat_signals", "structured_content", "word_count",
        ])
    )
    assert count == 16


@respx.mock
def test_audit_runs_without_error():
    respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_STUB_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    result = runner.invoke(app, ["audit", "https://example.com"])
    # All checks are SKIP stubs → score = 0 → exit 1 (below threshold 70)
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)  # clean exit, not a crash


@respx.mock
def test_audit_json_format():
    respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_STUB_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    result = runner.invoke(app, ["audit", "https://example.com", "--format", "json"])
    assert result.exit_code == 1
    assert '"url"' in result.output
    assert '"score"' in result.output


@respx.mock
def test_audit_output_file(tmp_path):
    respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_STUB_HTML))
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    out = tmp_path / "report.md"
    runner.invoke(app, ["audit", "https://example.com", "--output", str(out)])
    assert out.exists()
    assert "Pythia" in out.read_text()


def test_audit_missing_url():
    r = runner.invoke(app, ["audit"])
    assert r.exit_code != 0
