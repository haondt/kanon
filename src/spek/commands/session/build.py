from __future__ import annotations

import json as json_mod

import click

from spek.core.session import next_build_note_key
from ._helpers import load_session_or_exit, save_session_and_emit_hashes
from spek.commands._utils import read_text_arg_json


@click.group("build")
def session_build() -> None:
    """Manage build notes."""


@session_build.command("note")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def build_note(text: str, as_json: bool, input_json: bool) -> None:
    """Append a build note."""
    state, _ = load_session_or_exit()
    key = next_build_note_key(state)
    state.build.notes[key] = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


@session_build.command("unnote")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def build_unnote(key: str, as_json: bool) -> None:
    """Remove a build note by key."""
    state, _ = load_session_or_exit()
    if key not in state.build.notes:
        click.echo(f"Build note {key!r} not found.", err=True)
        raise SystemExit(1)
    del state.build.notes[key]
    save_session_and_emit_hashes(state, as_json, {"key": key})


@session_build.command("status")

@click.option("--json", "as_json", is_flag=True)
def build_status(as_json: bool) -> None:
    """Show build notes."""
    state, h = load_session_or_exit()
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "notes": dict(state.build.notes)}))
    else:
        for k, n in state.build.notes.items():
            click.echo(f"{k}: {n}")
