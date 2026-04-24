from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from . import __version__
from .checks import ALL_CHECKS
from .fetcher import fetch_page, fetch_robots
from .models import AuditContext
from .reporters.json_reporter import render_json
from .reporters.markdown import render_markdown
from .scoring import build_report

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
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save report to file"),
) -> None:
    """Audit a URL for GEO/AEO signals."""
    passed = asyncio.run(_run_audit(url, format, lang, threshold, output))
    raise typer.Exit(code=0 if passed else 1)


async def _run_audit(
    url: str, format: str, lang: str, threshold: int, output: Optional[str]
) -> bool:
    ctx = AuditContext(url=url, lang=lang)  # type: ignore[arg-type]

    ctx.html = await fetch_page(ctx)
    ctx.robots_txt = await fetch_robots(ctx)
    ctx.get_soup()

    results = []
    for check_cls in ALL_CHECKS:
        check = check_cls()
        result = await check.run(ctx)
        results.append(result)

    report = build_report(url, results, threshold=threshold, lang=lang)

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
