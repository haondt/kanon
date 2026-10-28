from __future__ import annotations

import json

import click

from kanon.commands.session._helpers import load_session_or_exit, save_session_and_emit_hashes
from kanon.commands._utils import fail, input_json_option, json_option, read_text_arg_json


@click.group("amend")
def session_amend() -> None:
    """Amend the current session goal or plan."""


@session_amend.command("goal")
@click.argument("text")

@json_option
@input_json_option
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

@json_option
@input_json_option
def amend_plan_step(key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Overwrite a plan step's text."""
    state, _ = load_session_or_exit()
    if key not in state.plan.steps:
        fail(f"Step {key!r} not found.")
    state.plan.steps[key].text = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


@amend_plan.command("note")
@click.argument("key")
@click.argument("text")

@json_option
@input_json_option
def amend_plan_note(key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Edit an existing plan note."""
    state, _ = load_session_or_exit()
    if key not in state.plan.notes:
        fail(f"Plan note {key!r} not found.")
    state.plan.notes[key] = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


@amend_plan.command("unnote")
@click.argument("key")

@json_option
def amend_plan_unnote(key: str, as_json: bool) -> None:
    """Remove a plan note by key."""
    state, _ = load_session_or_exit()
    if key not in state.plan.notes:
        fail(f"Plan note {key!r} not found.")
    del state.plan.notes[key]
    save_session_and_emit_hashes(state, as_json, {"key": key})


@session_amend.command("add-note")
@click.argument("text")

@json_option
@input_json_option
def amend_add_note(text: str, as_json: bool, input_json: bool) -> None:
    """Append an amendment note."""
    state, _ = load_session_or_exit()
    state.amendments.append(read_text_arg_json(text, input_json))
    save_session_and_emit_hashes(state, as_json)


@session_amend.command("status")

@json_option
def amend_status(as_json: bool) -> None:
    """Show amendments."""
    state, h = load_session_or_exit()
    if as_json:
        click.echo(json.dumps({"hash": h, "amendments": list(state.amendments)}))
    else:
        for a in state.amendments:
            click.echo(f"- {a}")
