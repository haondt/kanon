from __future__ import annotations

import json

import click

from ._helpers import load_session_or_exit, save_session_and_emit_hashes
from spek.commands._utils import read_text_arg_json


@click.group("amend")
def session_amend() -> None:
    """Amend the current session goal or plan."""


@session_amend.command("goal")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def amend_goal(text: str, as_json: bool, input_json: bool) -> None:
    """Overwrite the session goal."""
    state, _ = load_session_or_exit()
    state.goal = read_text_arg_json(text, input_json).strip()
    save_session_and_emit_hashes(state, as_json)

@session_amend.group("plan")
def amend_plan() -> None:
    """Amend plan steps or notes."""


@amend_plan.command("step")
@click.argument("key")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def amend_plan_step(key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Overwrite a plan step's text."""
    state, _ = load_session_or_exit()
    if key not in state.plan.steps:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    state.plan.steps[key].text = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


@amend_plan.command("note")
@click.argument("key")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def amend_plan_note(key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Edit an existing plan note."""
    state, _ = load_session_or_exit()
    if key not in state.plan.notes:
        click.echo(f"Plan note {key!r} not found.", err=True)
        raise SystemExit(1)
    state.plan.notes[key] = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


@amend_plan.command("unnote")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def amend_plan_unnote(key: str, as_json: bool) -> None:
    """Remove a plan note by key."""
    state, _ = load_session_or_exit()
    if key not in state.plan.notes:
        click.echo(f"Plan note {key!r} not found.", err=True)
        raise SystemExit(1)
    del state.plan.notes[key]
    save_session_and_emit_hashes(state, as_json, {"key": key})


@session_amend.command("add-note")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def amend_add_note(text: str, as_json: bool, input_json: bool) -> None:
    """Append an amendment note."""
    state, _ = load_session_or_exit()
    state.amendments.append(read_text_arg_json(text, input_json))
    save_session_and_emit_hashes(state, as_json)


@session_amend.command("status")

@click.option("--json", "as_json", is_flag=True)
def amend_status(as_json: bool) -> None:
    """Show amendments."""
    state, h = load_session_or_exit()
    if as_json:
        click.echo(json.dumps({"hash": h, "amendments": list(state.amendments)}))
    else:
        for a in state.amendments:
            click.echo(f"- {a}")
