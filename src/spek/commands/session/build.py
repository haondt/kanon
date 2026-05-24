from __future__ import annotations

import json as json_mod

import click

from spek.core.session import next_build_note_key
from ._helpers import _load, _save_and_emit_hashes
from spek.commands._utils import read_text_arg


@click.group("build")
def session_build() -> None:
    """Manage build notes."""


@session_build.command("note")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def build_note(text: str, project_root: str, as_json: bool) -> None:
    """Append a build note."""
    state, _, root = _load(project_root)
    key = next_build_note_key(state)
    state.build.notes[key] = read_text_arg(text).strip()
    _save_and_emit_hashes(state, root, as_json, {"key": key})


@session_build.command("unnote")
@click.argument("key")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def build_unnote(key: str, project_root: str, as_json: bool) -> None:
    """Remove a build note by key."""
    state, _, root = _load(project_root)
    if key not in state.build.notes:
        click.echo(f"Build note {key!r} not found.", err=True)
        raise SystemExit(1)
    del state.build.notes[key]
    _save_and_emit_hashes(state, root, as_json, {"key": key})


@session_build.command("status")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def build_status(project_root: str, as_json: bool) -> None:
    """Show build notes."""
    state, h, _ = _load(project_root)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "notes": dict(state.build.notes)}))
    else:
        for k, n in state.build.notes.items():
            click.echo(f"{k}: {n}")
