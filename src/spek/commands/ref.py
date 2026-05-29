from __future__ import annotations

import click
import json

from spek.core.config import SourcedResource
from spek.core.references import NormalizedTerms, Reference
from spek.core.sources import SourceResolver


@click.group()
def ref():
    """Search and read entries from the spek reference library."""


@ref.command("search")
@click.argument("terms", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
@click.option("--match-all", "match_all", is_flag=True, help="Require all terms to match (default: any term matches).")
@click.option("-n", "limit", type=int, default=10, help="Maximum results to return. 0 for unlimited.")
def ref_search(terms: tuple[str, ...], as_json: bool, match_all: bool, limit: int) -> None:
    """Search reference entries by keyword."""
    sources = SourceResolver.instance()
    normalized_terms = NormalizedTerms(list(terms))
    results: list[tuple[int, str, Reference]] = []

    for source_key, source in sources.items():
        for result in source.search_references(normalized_terms, limit, match_all):
            results.append((result.score(normalized_terms), SourcedResource(source_key, result.path).as_string, result))

    results.sort(key=lambda x: x[0], reverse=True)
    results = results[:limit] if limit > 0 else results

    if as_json:
        click.echo(json.dumps([
            {
                "name": s,
                "description": r.frontmatter.spek.description,
                "keywords": r.frontmatter.spek.keywords
            }
            for _, s, r in results]))
        return

    if not results:
        click.echo("No references found.")
        return

    for r in results:
        kw = ", ".join(r[2].frontmatter.spek.keywords)
        desc = r[2].frontmatter.spek.description or ""
        click.echo(f"{r[1]}  {desc}  [{kw}]")


@ref.command("read")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON.")
def ref_read(name: str, as_json: bool) -> None:
    """Read a reference entry by name."""
    sources = SourceResolver.instance()
    res = SourcedResource.parse(name)
    source = sources.try_resolve(res.source)
    if source is None:
        click.echo(f"Could not resolve source {res.source}")
        raise SystemExit(1)
    reference = source.hydrate_reference(res.path)

    if as_json:
        json_data = {
            "name": res.as_string,
            "description": reference.frontmatter.spek.description,
            "keywords": reference.frontmatter.spek.keywords,
            "content": reference.content,
        }
        click.echo(json.dumps(json_data))
        return

    click.echo(reference.content, nl=False)
