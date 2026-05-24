from __future__ import annotations

import click

from spek.core.session import PlanStep, next_plan_note_key
from ._helpers import _load, _save_and_emit_hashes
from spek.commands._utils import read_text_arg


@click.group("plan")
def session_plan() -> None:
    """Manage the session plan."""


@session_plan.command("status")
@click.option("--key", default=None)
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_status(key: str | None, project_root: str, as_json: bool) -> None:
    """Show plan status."""
    import json as json_mod
    state, h, _ = _load(project_root)
    if key:
        step = state.plan.steps.get(key)
        if step is None:
            click.echo(f"Step {key!r} not found.", err=True)
            raise SystemExit(1)
        if as_json:
            click.echo(json_mod.dumps({"hash": h, "key": key, **step.model_dump()}))
        else:
            mark = "✓" if step.done else " "
            click.echo(f"[{mark}] {key}: {step.text}")
        return

    if as_json:
        click.echo(json_mod.dumps({
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
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_add_step(key: str, text: str, project_root: str, as_json: bool) -> None:
    """Add a plan step."""
    state, _, root = _load(project_root)
    if key in state.plan.steps:
        click.echo(f"Step {key!r} already exists.", err=True)
        raise SystemExit(1)
    state.plan.steps[key] = PlanStep(text=read_text_arg(text).strip())
    _save_and_emit_hashes(state, root, as_json, {"key": key})


@session_plan.command("check")
@click.argument("key")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_check(key: str, project_root: str, as_json: bool) -> None:
    """Mark a plan step as done."""
    state, _, root = _load(project_root)
    step = state.plan.steps.get(key)
    if step is None:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    step.done = True
    _save_and_emit_hashes(state, root, as_json, {"key": key, "done": True})


@session_plan.command("uncheck")
@click.argument("key")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_uncheck(key: str, project_root: str, as_json: bool) -> None:
    """Mark a plan step as not done."""
    state, _, root = _load(project_root)
    step = state.plan.steps.get(key)
    if step is None:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    step.done = False
    _save_and_emit_hashes(state, root, as_json, {"key": key, "done": False})


@session_plan.command("note")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_note(text: str, project_root: str, as_json: bool) -> None:
    """Append a note to the plan."""
    state, _, root = _load(project_root)
    key = next_plan_note_key(state)
    state.plan.notes[key] = read_text_arg(text).strip()
    _save_and_emit_hashes(state, root, as_json, {"key": key})


