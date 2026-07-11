"""Command-line interface for CNKI automation.

Workflows:
    search        Search CNKI by keyword and save result list to JSON.
    read          Open a CNKI article detail page and save a TXT summary
                  containing GB/T 7714 citation and abstract.
    read-batch    Batch-open article detail pages and save TXT summaries.
"""

import sys
from pathlib import Path

import click

from . import config, reader, search, summarizer, utils
from .browser import managed_browser
from .citation import format_gb7714
from .search import load_results


def _build_summary_text(article: dict) -> str:
    """Combine citation and structured summary into the final TXT content."""
    citation = format_gb7714(article)
    summary = summarizer.summarize(
        article.get("text", ""),
        is_abstract_only=article.get("text_type") == "abstract",
    )
    lines = [
        f"标题：{article.get('title', '')}",
        f"作者：{', '.join(article.get('authors', []))}",
        f"来源：{article.get('source', '')}",
        f"年/期：{article.get('year', '')}({article.get('issue', '')})",
        f"页码：{article.get('pages', '')}",
        f"URL：{article.get('url', '')}",
        "",
        f"【GB/T 7714 引用】",
        citation,
        "",
        summary,
    ]
    return "\n".join(lines)


def _write_summary(article: dict, output_path: Path):
    """Write the summary TXT for a single article."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_build_summary_text(article), encoding="utf-8")


def _derive_output_name(article: dict, suffix: str = ".txt") -> str:
    """Create a safe filename from title and first author."""
    title = utils.sanitize_filename(article.get("title", "article"))
    authors = article.get("authors", [])
    author_part = utils.sanitize_filename(authors[0]) if authors else ""
    if author_part:
        return f"{title}_{author_part}{suffix}"
    return f"{title}{suffix}"


@click.group()
@click.option(
    "--headless/--no-headless",
    default=config.HEADLESS,
    help="Run browser in headless mode (default: headless to avoid blocking your desktop).",
)
@click.option(
    "--slow/--normal",
    default=False,
    help="Use slower delays (5-12s) to reduce detection risk (default: normal).",
)
@click.pass_context
def cli(ctx, headless, slow):
    """CNKI automation CLI: search and collect article abstracts with citations."""
    ctx.ensure_object(dict)
    ctx.obj["headless"] = headless
    ctx.obj["slow"] = slow


def _delay_range(ctx):
    """Return (min, max) delay seconds based on --slow flag."""
    if ctx.obj.get("slow"):
        return (5.0, 12.0)
    return (config.DELAY_MIN, config.DELAY_MAX)


@cli.command("search")
@click.argument("keyword")
@click.option("--pages", "-p", default=config.MAX_PAGES, type=int, help="Maximum pages to fetch.")
@click.option("--max-results", "-r", default=None, type=int, help="Maximum total results to collect.")
@click.option("--output", "-o", default="results.json", type=click.Path(), help="Path to save results.")
@click.pass_context
def search_cmd(ctx, keyword, pages, max_results, output):
    """Search CNKI by keyword and save results."""
    output_path = Path(output)
    delay_min, delay_max = _delay_range(ctx)
    with managed_browser(headless=ctx.obj["headless"]) as bm:
        results = search.search(bm.page, keyword, max_pages=pages, max_results=max_results)
        search.save_results(results, output_path)
        click.echo(f"Found {len(results)} results, saved to {output_path}")
        for r in results[:5]:
            click.echo(f"  - {r['title']} ({r['date']})")
        utils.random_delay(delay_min, delay_max)


@cli.command("read")
@click.option("--input", "-i", "input_path", default=None, type=click.Path(exists=True), help="Results JSON from search.")
@click.option("--index", "-n", default=0, type=int, help="Zero-based index of result to read.")
@click.option("--url", "-u", default=None, help="CNKI detail URL to read directly.")
@click.option("--output", "-o", default="summary.txt", type=click.Path(), help="Path to save TXT summary.")
@click.pass_context
def read_cmd(ctx, input_path, index, url, output):
    """Open a CNKI article detail page and save a TXT summary."""
    detail_url = None
    if url:
        detail_url = url
    elif input_path:
        results = load_results(Path(input_path))
        if not results:
            click.echo("No results found.", err=True)
            sys.exit(1)
        if index < 0 or index >= len(results):
            click.echo(f"Index {index} out of range (0-{len(results)-1}).", err=True)
            sys.exit(1)
        detail_url = results[index].get("detail_url")
        if not detail_url:
            click.echo(f"Result {index} has no detail URL.", err=True)
            sys.exit(1)
    else:
        click.echo("Must provide either --input/--index or --url.", err=True)
        sys.exit(1)

    expected_title = ""
    expected_source = ""
    expected_year = ""
    if input_path:
        expected_title = results[index].get("title", "")
        expected_source = results[index].get("source", "")
        expected_year = results[index].get("year", "")

    click.echo(f"Opening detail page: {detail_url}")
    with managed_browser(headless=ctx.obj["headless"]) as bm:
        article = reader.read_article(
            bm.page, detail_url,
            expected_title=expected_title,
            expected_source=expected_source,
            expected_year=expected_year,
        )
        _write_summary(article, Path(output))
        click.echo(f"Summary saved to {output}")
        click.echo(f"  Title: {article['title']}")
        click.echo(f"  Citation: {format_gb7714(article)}")
        if article.get("warnings"):
            for warning in article["warnings"]:
                click.echo(f"  Warning: {warning}", err=True)


@cli.command("read-batch")
@click.option("--input", "-i", "input_path", default="results.json", type=click.Path(exists=True), help="Results JSON from search.")
@click.option("--output-dir", "-d", default="summaries", type=click.Path(), help="Directory for TXT summaries.")
@click.option("--limit", "-l", default=None, type=int, help="Maximum number of articles to read.")
@click.option("--start", "-s", default=0, type=int, help="Start index (inclusive).")
@click.option("--end", "-e", default=None, type=int, help="End index (exclusive).")
@click.pass_context
def read_batch_cmd(ctx, input_path, output_dir, limit, start, end):
    """Batch-open CNKI article detail pages and save TXT summaries."""
    results = load_results(Path(input_path))
    if not results:
        click.echo("No results found.", err=True)
        sys.exit(1)

    end = end if end is not None else len(results)
    if start < 0 or start > len(results):
        click.echo(f"Start index {start} out of range (0-{len(results)}).", err=True)
        sys.exit(1)
    if end < start or end > len(results):
        click.echo(f"End index {end} out of range.", err=True)
        sys.exit(1)

    batch = results[start:end]
    if limit is not None:
        batch = batch[:limit]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Batch reading {len(batch)} articles...")
    delay_min, delay_max = _delay_range(ctx)
    with managed_browser(headless=ctx.obj["headless"]) as bm:
        for idx, item in enumerate(batch, start=start):
            detail_url = item.get("detail_url")
            if not detail_url:
                click.echo(f"[{idx}] skipped: no detail URL", err=True)
                continue
            click.echo(f"[{idx}] reading: {item.get('title', detail_url)}")
            try:
                article = reader.read_article(
                    bm.page,
                    detail_url,
                    expected_title=item.get("title", ""),
                    expected_source=item.get("source", ""),
                    expected_year=item.get("year", ""),
                )
                out_name = _derive_output_name(article)
                out_path = output_dir / out_name
                # Avoid overwriting duplicates by appending an index.
                if out_path.exists():
                    stem = out_path.stem
                    out_path = output_dir / f"{stem}_{idx}{out_path.suffix}"
                _write_summary(article, out_path)
                click.echo(f"[{idx}] saved: {out_path}")
                if article.get("warnings"):
                    for warning in article["warnings"]:
                        click.echo(f"[{idx}] warning: {warning}", err=True)
                utils.random_delay(delay_min, delay_max)
            except Exception as exc:
                click.echo(f"[{idx}] failed: {exc}", err=True)
                continue

    click.echo(f"Done. Summaries saved to {output_dir}")


if __name__ == "__main__":
    cli()
