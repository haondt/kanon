from __future__ import annotations

import json as json_mod

import click

from ._helpers import _load, _save_and_emit_hashes


@click.group("stance")
def session_stance() -> None:
    """Manage session stance."""


@session_stance.command("set")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def stance_set(name: str, project_root: str, as_json: bool) -> None:
    """Set the active stance."""
    state, _, root = _load(project_root)
    state.stance = name.strip()
    _save_and_emit_hashes(state, root, as_json, {"stance": state.stance})


@session_stance.command("clear")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def stance_clear(project_root: str, as_json: bool) -> None:
    """Clear the active stance."""
    state, _, root = _load(project_root)
    state.stance = None
    _save_and_emit_hashes(state, root, as_json)


@session_stance.command("status")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def stance_status(project_root: str, as_json: bool) -> None:
    """Show the current stance."""
    state, h, _ = _load(project_root)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "stance": state.stance}))
    else:
        click.echo(state.stance or "(none)")
