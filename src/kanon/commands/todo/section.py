from __future__ import annotations

import json

import click

from kanon.core.todo import TodoSection
from ._helpers import save_todo_file_and_emit_hashes, load_todo_file


@click.group("section")
def todo_section() -> None:
    """Manage backlog sections."""


@todo_section.command("status")

@click.option("--json", "as_json", is_flag=True)
def section_status(as_json: bool) -> None:
    """List all sections with item counts."""
    state, h = load_todo_file()
    if as_json:
        click.echo(json.dumps({
            "hash": h,
            "sections": {k: {"name": s.name, "count": len(s.items)} for k, s in state.sections.items()},
        }))
        return
    for k, s in state.sections.items():
        click.echo(f"  {k}: {s.name} ({len(s.items)} item(s))")


@todo_section.command("search")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
def section_search(text: str, as_json: bool) -> None:
    """Search section names (case-insensitive substring)."""
    state, h = load_todo_file()
    matches = {k: s for k, s in state.sections.items() if text.lower() in s.name.lower()}
    if as_json:
        click.echo(json.dumps({
            "hash": h,
            "sections": {k: {"name": s.name, "count": len(s.items)} for k, s in matches.items()},
        }))
        return
    for k, s in matches.items():
        click.echo(f"  {k}: {s.name} ({len(s.items)} item(s))")


@todo_section.command("add")
@click.argument("key")
@click.argument("name")
@click.option("--allow-exists", is_flag=True, help="No-op if section already exists.")

@click.option("--json", "as_json", is_flag=True)
def section_add(key: str, name: str, allow_exists: bool, as_json: bool) -> None:
    """Add a new section."""
    state, _ = load_todo_file(True)
    if key in state.sections:
        if allow_exists:
            if as_json:
                click.echo(json.dumps({"key": key, "existed": True}))
            else:
                click.echo(f"Section {key!r} already exists — no change.")
            return
        click.echo(f"Section {key!r} already exists. Use --allow-exists to skip.", err=True)
        raise SystemExit(1)
    state.sections[key] = TodoSection(name=name)
    save_todo_file_and_emit_hashes(state, as_json, {"key": key})
