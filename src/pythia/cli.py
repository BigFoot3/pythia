from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from . import __version__
from .api import audit_url
from .checks import ALL_CHECKS
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
        console.print(output_str)
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
def version() -> None:
    """Show pythia-geo version."""
    console.print(f"pythia-geo {__version__}")
