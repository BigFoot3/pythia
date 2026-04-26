from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from . import __version__
from .api import audit_url, compare_urls
from .checks import ALL_CHECKS
from .fixers import generate_fixes
from .generators import generate_llms_txt
from .reporters.compare import render_compare_json, render_compare_markdown
from .reporters.fixes import render_fixes_json, render_fixes_markdown
from .reporters.json_reporter import render_json
from .reporters.markdown import render_markdown

app = typer.Typer(
    name="pythia",
    help="The oracle that tells you how AIs see your site — GEO/AEO audit CLI",
    add_completion=False,
)
console = Console()


@app.command()
def audit(
    url: str = typer.Argument(..., help="URL to audit"),
    format: str = typer.Option("md", "--format", "-f", help="Output format: md or json"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en or fr"),
    threshold: int = typer.Option(70, "--threshold", "-t", help="Minimum passing score (exit 1 if below)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save report to file"),
    page_type: str = typer.Option(
        "auto", "--page-type", "-p",
        help="Page type: auto, article, homepage, doc (auto detects from URL path)",
    ),
) -> None:
    """Audit a URL for GEO/AEO signals."""
    passed = asyncio.run(_run_audit(url, format, lang, threshold, output, page_type))
    raise typer.Exit(code=0 if passed else 1)


async def _run_audit(
    url: str, format: str, lang: str, threshold: int, output: str | None, page_type: str = "auto"
) -> bool:
    report = await audit_url(url, lang=lang, page_type=page_type, threshold=threshold)

    if format == "json":
        output_str = render_json(report)
    else:
        output_str = render_markdown(report)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_str)
        console.print(f"Report saved to [green]{output}[/green]")
    elif format == "json":
        print(output_str)
    else:
        console.print(Markdown(output_str))

    return report.passed


@app.command(name="list-checks")
def list_checks() -> None:
    """List all available checks."""
    table = Table(title="Pythia — available checks")
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Weight", justify="right")
    for check_cls in ALL_CHECKS:
        c = check_cls()
        table.add_row(c.name, c.category, str(c.weight))
    console.print(table)


@app.command()
def fix(
    url: str = typer.Argument(..., help="URL to audit and fix"),
    format: str = typer.Option("md", "--format", "-f", help="Output format: md or json"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en or fr"),
    page_type: str = typer.Option("auto", "--page-type", "-p", help="Page type: auto, article, homepage, doc"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save report to file"),
) -> None:
    """Generate ready-to-paste HTML fixes for all FAIL/WARN checks."""
    asyncio.run(_run_fix(url, format, lang, page_type, output))


async def _run_fix(url: str, format: str, lang: str, page_type: str, output: str | None) -> None:
    report = await audit_url(url, lang=lang, page_type=page_type)
    fixes = generate_fixes(report)

    if format == "json":
        output_str = render_fixes_json(report, fixes)
    else:
        output_str = render_fixes_markdown(report, fixes)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_str)
        console.print(f"Fixes saved to [green]{output}[/green]")
    elif format == "json":
        print(output_str)
    else:
        console.print(Markdown(output_str))


@app.command()
def compare(
    url1: str = typer.Argument(..., help="First URL to audit"),
    url2: str = typer.Argument(..., help="Second URL to compare against"),
    format: str = typer.Option("md", "--format", "-f", help="Output format: md or json"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en or fr"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save report to file"),
) -> None:
    """Compare two URLs check by check."""
    asyncio.run(_run_compare(url1, url2, format, lang, output))


async def _run_compare(url1: str, url2: str, format: str, lang: str, output: str | None) -> None:
    cmp = await compare_urls(url1, url2, lang=lang)

    if format == "json":
        output_str = render_compare_json(cmp)
    else:
        output_str = render_compare_markdown(cmp)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_str)
        console.print(f"Comparison saved to [green]{output}[/green]")
    elif format == "json":
        print(output_str)
    else:
        console.print(Markdown(output_str))


@app.command(name="generate-llms")
def generate_llms(
    url: str = typer.Argument(..., help="Site URL (sitemap will be auto-discovered)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file (default: print to stdout)"),
    max_pages: int = typer.Option(50, "--max-pages", "-n", help="Maximum number of pages to crawl"),
) -> None:
    """Generate a ready-to-deploy llms.txt by crawling the site's sitemap."""
    content = asyncio.run(generate_llms_txt(url, max_pages=max_pages))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]llms.txt saved to {output}[/green]")
    else:
        console.print(content)


@app.command()
def version() -> None:
    """Show pythia-geo version."""
    console.print(f"pythia-geo {__version__}")
