import pytest

from pythia.models import AuditContext

GOOD_PAGE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>How to Build a Python CLI Tool in 2024</title>
  <meta name="description" content="A comprehensive guide to building command-line tools with Python, typer, and rich. Covers packaging, distribution, and CI.">
  <meta property="og:title" content="How to Build a Python CLI Tool">
  <meta property="og:description" content="Step-by-step guide with examples.">
  <meta property="og:type" content="article">
  <script type="application/ld+json">
  {"@context": "https://schema.org", "@type": "Article", "name": "How to Build a Python CLI Tool"}
  </script>
</head>
<body>
  <article>
    <h1>How to Build a Python CLI Tool in 2024</h1>
    <p>By <span class="author">Jane Smith</span> — <time datetime="2024-03-15">March 15, 2024</time></p>
    <h2>Prerequisites</h2>
    <p>Before we start, make sure you have:</p>
    <ul>
      <li>Python 3.11+</li>
      <li>pip or uv</li>
    </ul>
    <h2>Step by step</h2>
    <h3>Install typer</h3>
    <p>Run the following command:</p>
    <h2>FAQ</h2>
    <dl>
      <dt>What is a CLI?</dt>
      <dd>A command-line interface.</dd>
      <dt>Why use typer?</dt>
      <dd>It reduces boilerplate.</dd>
    </dl>
    <h2>Summary</h2>
    <table>
      <tr><th>Tool</th><th>Purpose</th></tr>
      <tr><td>typer</td><td>CLI framework</td></tr>
    </table>
  </article>
</body>
</html>"""

BAD_PAGE_HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Hi</title>
</head>
<body>
  <h1>Welcome</h1>
  <h1>Home</h1>
  <h3>Skipped level</h3>
  <p>Some text without structure.</p>
</body>
</html>"""


@pytest.fixture
def good_html() -> str:
    return GOOD_PAGE_HTML


@pytest.fixture
def bad_html() -> str:
    return BAD_PAGE_HTML


@pytest.fixture
def ctx(good_html: str) -> AuditContext:
    c = AuditContext(url="https://example.com", html=good_html)
    c.get_soup()
    return c


@pytest.fixture
def ctx_fr(good_html: str) -> AuditContext:
    c = AuditContext(url="https://example.com", html=good_html, lang="fr")
    c.get_soup()
    return c


@pytest.fixture
def ctx_bad(bad_html: str) -> AuditContext:
    c = AuditContext(url="https://example.com", html=bad_html)
    c.get_soup()
    return c
