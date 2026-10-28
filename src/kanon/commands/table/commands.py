from __future__ import annotations

import json
from typing import Any, get_args

import click

from kanon.commands._utils import fail, input_json_option, json_option, read_text_arg_json
from kanon.core.errors import KanonError
from kanon.core.table import TableState, TableStatus, key_order, status_label
from kanon.commands.table._helpers import emit_no_change, save_table_file_and_emit_hashes


@click.command("status")
@click.argument("key", required=False)
@json_option
def table_status(key: str | None, as_json: bool) -> None:
    """Show the table, or one item with its summary and neighbors."""
    state, h = TableState.load()

    if key is None:
        if as_json:
            click.echo(json.dumps({
                "hash": h,
                "items": {k: i.model_dump() for k, i in sorted(state.items.items(), key=lambda kv: key_order(kv[0]))},
                "edges": [[e.a, e.b] for e in state.edges],
            }))
        else:
            click.echo(state.render_graph())
        return

    if key not in state.items:
        valid = ", ".join(sorted(state.items, key=key_order)) or "none"
        fail(f"No item {key!r}. Valid keys: {valid}")
    item = state.items[key]
    near = [(n, state.items[n]) for n in state.neighbors(key)]

    if as_json:
        click.echo(json.dumps({
            "hash": h,
            "key": key,
            **item.model_dump(),
            "neighbors": [{"key": n, "title": i.title, "status": i.status} for n, i in near],
        }))
        return

    click.echo(f"{status_label(item.status)}  {key}:{{{item.title}}}")
    click.echo("\nSummary")
    click.echo("\n".join(f"  {line}" for line in item.summary.splitlines()) if item.summary else "  (none)")
    click.echo("\nNeighbors")
    if near:
        for n, i in near:
            click.echo(f"  {status_label(i.status)}  {n}:{{{i.title}}}")
    else:
        click.echo("  none")


@click.command("add")
@click.argument("title")
@click.option("--summary", default="", help="Item summary; pass '-' to read from stdin.")
@click.option("--link", "links", multiple=True, help="Key of an existing item to link to.")
@json_option
@input_json_option
def table_add(title: str, summary: str, links: tuple[str, ...], as_json: bool, input_json: bool) -> None:
    """Add an open item. No-op if an item with the same title exists."""
    state, h = TableState.load()
    try:
        key, created = state.add(
            read_text_arg_json(title, input_json),
            read_text_arg_json(summary, input_json) if summary else "",
            list(links),
        )
    except KanonError as e:
        fail(e)
    if not created:
        emit_no_change(f"Item {key!r} already has this title — no change.", as_json, h, {"key": key})
        return
    save_table_file_and_emit_hashes(state, as_json, {"key": key})


@click.command("edit")
@click.argument("key")
@click.option("--title", default=None)
@click.option("--summary", default=None, help="New summary; pass '-' to read from stdin.")
@json_option
@input_json_option
def table_edit(key: str, title: str | None, summary: str | None, as_json: bool, input_json: bool) -> None:
    """Rewrite an item's title and/or summary."""
    if title is None and summary is None:
        fail("Provide --title and/or --summary.")
    state, _ = TableState.load()
    try:
        state.edit_item(
            key,
            read_text_arg_json(title, input_json) if title is not None else None,
            read_text_arg_json(summary, input_json) if summary is not None else None,
        )
    except KanonError as e:
        fail(e)
    save_table_file_and_emit_hashes(state, as_json)


@click.command("set-status")
@click.argument("key")
@click.argument("status", type=click.Choice(list(get_args(TableStatus))))
@json_option
def table_set_status(key: str, status: TableStatus, as_json: bool) -> None:
    """Set an item's status. Setting active demotes the current active item to open."""
    state, _ = TableState.load()
    try:
        demoted = state.set_status(key, status)
    except KanonError as e:
        fail(e)
    extra: dict[str, Any] = {"demoted": demoted} if demoted else {}
    save_table_file_and_emit_hashes(state, as_json, extra)


@click.command("link")
@click.argument("a")
@click.argument("b")
@json_option
def table_link(a: str, b: str, as_json: bool) -> None:
    """Add an undirected edge between two items."""
    state, h = TableState.load()
    try:
        created = state.link_items(a, b)
    except KanonError as e:
        fail(e)
    if not created:
        emit_no_change(f"{a!r} and {b!r} are already linked — no change.", as_json, h)
        return
    save_table_file_and_emit_hashes(state, as_json)


@click.command("unlink")
@click.argument("a")
@click.argument("b")
@json_option
def table_unlink(a: str, b: str, as_json: bool) -> None:
    """Remove the edge between two items."""
    state, _ = TableState.load()
    try:
        state.unlink_items(a, b)
    except KanonError as e:
        fail(e)
    save_table_file_and_emit_hashes(state, as_json)


@click.command("merge")
@click.argument("keep")
@click.argument("absorb")
@json_option
def table_merge(keep: str, absorb: str, as_json: bool) -> None:
    """Fold ABSORB into KEEP: edges unioned, summaries joined, ABSORB's key retired."""
    state, _ = TableState.load()
    try:
        state.merge_items(keep, absorb)
    except KanonError as e:
        fail(e)
    save_table_file_and_emit_hashes(state, as_json, {"key": keep})


@click.command("remove")
@click.argument("key")
@json_option
def table_remove(key: str, as_json: bool) -> None:
    """Delete an item and its edges."""
    state, _ = TableState.load()
    try:
        state.remove_item(key)
    except KanonError as e:
        fail(e)
    save_table_file_and_emit_hashes(state, as_json)


@click.command("clear")
@json_option
def table_clear(as_json: bool) -> None:
    """Empty the table."""
    existed = TableState.clear()
    if as_json:
        click.echo(json.dumps({"cleared": existed}))
    else:
        click.echo("Table cleared." if existed else "Table is already empty.")


@click.command("lint")
@json_option
def table_lint(as_json: bool) -> None:
    """Lint the table file."""
    state, h = TableState.load()
    issues = state.lint()
    if as_json:
        click.echo(json.dumps({"hash": h, "issues": issues}))
    elif issues:
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("No issues found.")
