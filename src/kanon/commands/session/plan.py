from __future__ import annotations

import click

from kanon.core.session import PlanStep, next_plan_note_key
from ._helpers import load_session_or_exit, save_session_and_emit_hashes
from kanon.commands._utils import read_text_arg_json


@click.group("plan")
def session_plan() -> None:
    """Manage the session plan."""


@session_plan.command("status")
@click.option("--key", default=None)

@click.option("--json", "as_json", is_flag=True)
def plan_status(key: str | None, as_json: bool) -> None:
    """Show plan status."""
    import json
    state, h = load_session_or_exit()
    if key:
        step = state.plan.steps.get(key)
        if step is None:
            click.echo(f"Step {key!r} not found.", err=True)
            raise SystemExit(1)
        if as_json:
            click.echo(json.dumps({"hash": h, "key": key, **step.model_dump()}))
        else:
            mark = "✓" if step.done else " "
            click.echo(f"[{mark}] {key}: {step.text}")
        return

    if as_json:
        click.echo(json.dumps({
            "hash": h,
            "steps": {k: v.model_dump() for k, v in state.plan.steps.items()},
            "notes": dict(state.plan.notes),
        }))
        return

    for k, s in state.plan.steps.items():
        mark = "✓" if s.done else " "
        click.echo(f"[{mark}] {k}: {s.text}")
    for k, n in state.plan.notes.items():
        click.echo(f"  note {k}: {n}")


@session_plan.command("add-step")
@click.argument("key")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def plan_add_step(key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Add a plan step."""
    state, _ = load_session_or_exit()
    if key in state.plan.steps:
        click.echo(f"Step {key!r} already exists.", err=True)
        raise SystemExit(1)
    state.plan.steps[key] = PlanStep(text=read_text_arg_json(text, input_json))
    save_session_and_emit_hashes(state, as_json, {"key": key})


@session_plan.command("check")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def plan_check(key: str, as_json: bool) -> None:
    """Mark a plan step as done."""
    state, _ = load_session_or_exit()
    step = state.plan.steps.get(key)
    if step is None:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    step.done = True
    save_session_and_emit_hashes(state, as_json, {"key": key, "done": True})


@session_plan.command("uncheck")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def plan_uncheck(key: str, as_json: bool) -> None:
    """Mark a plan step as not done."""
    state, _ = load_session_or_exit()
    step = state.plan.steps.get(key)
    if step is None:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    step.done = False
    save_session_and_emit_hashes(state, as_json, {"key": key, "done": False})


@session_plan.command("note")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def plan_note(text: str, as_json: bool, input_json: bool) -> None:
    """Append a note to the plan."""
    state, _ = load_session_or_exit()
    key = next_plan_note_key(state)
    state.plan.notes[key] = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"key": key})


