from __future__ import annotations

import json as json_mod

import click

from spek.core.repo import spek_repo_path
from spek.core.references import read_reference, search_references


@click.group()
def ref():
    """Search and read entries from the spek reference library."""


@ref.command("search")
@click.argument("query")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def ref_search(query: str, as_json: bool) -> None:
    """Search reference entries by keyword."""
    repo_path = spek_repo_path()
    results = search_references(repo_path, query)

    if as_json:
        click.echo(json_mod.dumps([r.model_dump(exclude_none=True) for r in results]))
        return

    if not results:
        click.echo("No references found.")
        return

    for r in results:
        kw = ", ".join(r.keywords)
        desc = r.description or ""
        click.echo(f"{r.name}  {desc}  [{kw}]")


@ref.command("read")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON.")
def ref_read(name: str, as_json: bool) -> None:
    """Read a reference entry by name."""
    repo_path = spek_repo_path()
    try:
        result = read_reference(repo_path, name)
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    if as_json:
        click.echo(result.model_dump_json(exclude_none=True))
        return

    click.echo(result.content, nl=False)
