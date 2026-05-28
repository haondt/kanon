from __future__ import annotations

import json

import click

from ._helpers import load_session_or_exit, save_session_and_emit_hashes
from spek.commands._utils import read_text_arg


@click.group("detour")
def session_detour() -> None:
    """Manage detours."""


@session_detour.command("add")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
def detour_add(text: str, as_json: bool) -> None:
    """Record a detour."""
    state, _ = load_session_or_exit()
    state.detours.append(read_text_arg(text))
    save_session_and_emit_hashes(state, as_json)


@session_detour.command("status")

@click.option("--json", "as_json", is_flag=True)
def detour_status(as_json: bool) -> None:
    """Show detours."""
    state, h = load_session_or_exit()
    if as_json:
        click.echo(json.dumps({"hash": h, "detours": list(state.detours)}))
    else:
        for d in state.detours:
            click.echo(f"- {d}")
