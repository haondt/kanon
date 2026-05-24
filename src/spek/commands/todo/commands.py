from __future__ import annotations

import json as json_mod
from typing import Any

import click

from spek.core.todo import lint_todo
from ._helpers import _load
from spek.commands._utils import read_text_arg


@click.command("status")
@click.argument("text", required=False)
@click.option("--section", default=None)
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def todo_status(text: str | None, section: str | None, project_root: str, as_json: bool) -> None:
    """Show backlog items, optionally filtered by section or substring."""
    state, h, _ = _load(project_root)

    sections = {k: v for k, v in state.sections.items() if section is None or k == section}
    if section and section not in state.sections:
        click.echo(f"Section {section!r} not found.", err=True)
        raise SystemExit(1)

    if as_json:
        result: dict[str, Any] = {"hash": h, "sections": {}}
        for k, s in sections.items():
            items = s.items if text is None else [i for i in s.items if text.lower() in i.lower()]
            result["sections"][k] = {"name": s.name, "items": items}
        click.echo(json_mod.dumps(result))
        return

    for k, s in sections.items():
        items = s.items if text is None else [i for i in s.items if text.lower() in i.lower()]
        if not items:
            continue
        click.echo(f"## {s.name}")
        for item in items:
            click.echo(f"  - {item}")


@click.command("search")
@click.argument("terms", nargs=-1, required=True)
@click.option("--section", default=None)
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def todo_search(terms: tuple[str, ...], section: str | None, project_root: str, as_json: bool) -> None:
    """Search backlog items (all terms must match, case-insensitive)."""
    state, h, _ = _load(project_root)

    sections = {k: v for k, v in state.sections.items() if section is None or k == section}

    def _matches(item: str) -> bool:
        lower = item.lower()
        return all(t.lower() in lower for t in terms)

    if as_json:
        result: dict[str, Any] = {"hash": h, "sections": {}}
        for k, s in sections.items():
            matched = [i for i in s.items if _matches(i)]
            if matched:
                result["sections"][k] = {"name": s.name, "items": matched}
        click.echo(json_mod.dumps(result))
        return

    for k, s in sections.items():
        matched = [i for i in s.items if _matches(i)]
        if not matched:
            continue
        click.echo(f"## {s.name}")
        for item in matched:
            click.echo(f"  - {item}")


@click.command("add")
@click.argument("text")
@click.option("--section", required=True, help="Section key.")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def todo_add(text: str, section: str, project_root: str, as_json: bool) -> None:
    """Add an item to a section."""
    from ._helpers import _save_and_emit
    state, _, root = _load(project_root)
    if section not in state.sections:
        click.echo(f"Section {section!r} not found. Use 'spek todo section add' to create it.", err=True)
        raise SystemExit(1)
    state.sections[section].items.append(read_text_arg(text).strip())
    _save_and_emit(state, root, as_json)


@click.command("remove")
@click.argument("text")
@click.option("--section", required=True, help="Section key.")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def todo_remove(text: str, section: str, project_root: str, as_json: bool) -> None:
    """Remove an item from a section (exact match). Removes section if empty."""
    from ._helpers import _save_and_emit
    state, _, root = _load(project_root)
    text = read_text_arg(text).strip()
    if section not in state.sections:
        click.echo(f"Section {section!r} not found.", err=True)
        raise SystemExit(1)
    sec = state.sections[section]
    if text not in sec.items:
        click.echo(f"Item not found in section {section!r}: {text!r}", err=True)
        raise SystemExit(1)
    sec.items.remove(text)
    if not sec.items:
        del state.sections[section]
    _save_and_emit(state, root, as_json)


@click.command("lint")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def todo_lint(project_root: str, as_json: bool) -> None:
    """Lint the todo file."""
    state, h, _ = _load(project_root)
    issues = lint_todo(state)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "issues": issues}))
    else:
        if issues:
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("No issues found.")
