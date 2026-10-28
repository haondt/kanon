from __future__ import annotations

import json

import click

from kanon.commands.session._helpers import load_session_or_exit, save_session_and_emit_hashes
from kanon.commands._utils import json_option


@click.group("stance")
def session_stance() -> None:
    """Manage session stance."""


@session_stance.command("set")
@click.argument("name")

@json_option
def stance_set(name: str, as_json: bool) -> None:
    """Set the active stance."""
    state, _ = load_session_or_exit()
    state.stance = name.strip()
    save_session_and_emit_hashes(state, as_json, {"stance": state.stance})


@session_stance.command("clear")

@json_option
def stance_clear(as_json: bool) -> None:
    """Clear the active stance."""
    state, _ = load_session_or_exit()
    state.stance = None
    save_session_and_emit_hashes(state, as_json)


@session_stance.command("status")

@json_option
def stance_status(as_json: bool) -> None:
    """Show the current stance."""
    state, h = load_session_or_exit()
    if as_json:
        click.echo(json.dumps({"hash": h, "stance": state.stance}))
    else:
        click.echo(state.stance or "(none)")
