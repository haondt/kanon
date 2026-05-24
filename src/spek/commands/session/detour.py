from __future__ import annotations

import json as json_mod

import click

from ._helpers import _load, _save_and_emit_hashes


@click.group("detour")
def session_detour() -> None:
    """Manage detours."""


@session_detour.command("add")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def detour_add(text: str, project_root: str, as_json: bool) -> None:
    """Record a detour."""
    state, _, root = _load(project_root)
    state.detours.append(text.strip())
    _save_and_emit_hashes(state, root, as_json)


@session_detour.command("status")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def detour_status(project_root: str, as_json: bool) -> None:
    """Show detours."""
    state, h, _ = _load(project_root)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "detours": list(state.detours)}))
    else:
        for d in state.detours:
            click.echo(f"- {d}")
