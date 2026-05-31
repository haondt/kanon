from __future__ import annotations

import json as json_mod
from typing import Any

import click

from spek.core.plan import (
    PlanFile,
    PlanStep,
    SplitEntry,
    create_plan,
    create_split,
    index_path,
    load_split_index,
    next_note_key,
    parse_plan_ref,
    save_split_index,
)
from spek.commands._utils import read_text_arg, read_text_arg_json
from ._helpers import _load, _root, _save_and_emit


@click.group("plan")
def plan() -> None:
    """Manage standalone plan files."""


@plan.command("create")
@click.argument("name")
@click.argument("goal")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_create(name: str, goal: str, project_root: str, as_json: bool) -> None:
    """Create a new plan file."""
    root = _root(project_root)
    try:
        split, bare = parse_plan_ref(name)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if split is not None:
        if not index_path(root, split).exists():
            click.echo(f"Split {split!r} does not exist. Run 'spek split create {split} <goal>' first.", err=True)
            raise SystemExit(1)

    try:
        plan_obj, h = create_plan(read_text_arg(goal).strip(), root, name)
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    if split is not None:
        index, _ = load_split_index(root, split)
        index.plans[bare] = SplitEntry(status="pending")
        save_split_index(index, root, split)

    if as_json:
        click.echo(json_mod.dumps({"hash": h, "goal": plan_obj.goal}))
    else:
        click.echo(f"Plan created. hash: {h}")


@plan.command("read")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_read(name: str, project_root: str, as_json: bool) -> None:
    """Print a plan's goal, steps, and notes."""
    plan_obj, h, _ = _load(name, project_root)
    if as_json:
        click.echo(json_mod.dumps({
            "hash": h,
            "goal": plan_obj.goal,
            "steps": {k: v.model_dump() for k, v in plan_obj.steps.items()},
            "notes": dict(plan_obj.notes),
        }))
        return
    click.echo(f"goal: {plan_obj.goal}")
    for k, s in plan_obj.steps.items():
        mark = "✓" if s.done else " "
        click.echo(f"  [{mark}] {k}: {s.text}")
    for k, n in plan_obj.notes.items():
        click.echo(f"  note {k}: {n}")


@plan.command("goal")
@click.argument("name")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_goal(name: str, text: str, project_root: str, as_json: bool) -> None:
    """Overwrite the plan goal."""
    plan_obj, _, root = _load(name, project_root)
    plan_obj.goal = read_text_arg(text).strip()
    _save_and_emit(plan_obj, root, name, as_json)


@plan.command("add-step")
@click.argument("name")
@click.argument("key")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True)
def plan_add_step(name: str, key: str, text: str, project_root: str, as_json: bool, input_json: bool) -> None:
    """Add a step to the plan."""
    plan_obj, _, root = _load(name, project_root)
    if key in plan_obj.steps:
        click.echo(f"Step {key!r} already exists.", err=True)
        raise SystemExit(1)
    plan_obj.steps[key] = PlanStep(text=read_text_arg_json(text, input_json).strip())
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})


@plan.command("edit-step")
@click.argument("name")
@click.argument("key")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True)
def plan_edit_step(name: str, key: str, text: str, project_root: str, as_json: bool, input_json: bool) -> None:
    """Overwrite a step's text."""
    plan_obj, _, root = _load(name, project_root)
    if key not in plan_obj.steps:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    plan_obj.steps[key].text = read_text_arg_json(text, input_json).strip()
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})


@plan.command("remove-step")
@click.argument("name")
@click.argument("key")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_remove_step(name: str, key: str, project_root: str, as_json: bool) -> None:
    """Delete a step from the plan."""
    plan_obj, _, root = _load(name, project_root)
    if key not in plan_obj.steps:
        click.echo(f"Step {key!r} not found.", err=True)
        raise SystemExit(1)
    del plan_obj.steps[key]
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})


@plan.command("note")
@click.argument("name")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True)
def plan_note(name: str, text: str, project_root: str, as_json: bool, input_json: bool) -> None:
    """Append a note to the plan."""
    plan_obj, _, root = _load(name, project_root)
    key = next_note_key(plan_obj)
    plan_obj.notes[key] = read_text_arg_json(text, input_json).strip()
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})


@plan.command("edit-note")
@click.argument("name")
@click.argument("key")
@click.argument("text")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True)
def plan_edit_note(name: str, key: str, text: str, project_root: str, as_json: bool, input_json: bool) -> None:
    """Overwrite a note."""
    plan_obj, _, root = _load(name, project_root)
    if key not in plan_obj.notes:
        click.echo(f"Note {key!r} not found.", err=True)
        raise SystemExit(1)
    plan_obj.notes[key] = read_text_arg_json(text, input_json).strip()
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})


@plan.command("remove-note")
@click.argument("name")
@click.argument("key")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def plan_remove_note(name: str, key: str, project_root: str, as_json: bool) -> None:
    """Delete a note from the plan."""
    plan_obj, _, root = _load(name, project_root)
    if key not in plan_obj.notes:
        click.echo(f"Note {key!r} not found.", err=True)
        raise SystemExit(1)
    del plan_obj.notes[key]
    _save_and_emit(plan_obj, root, name, as_json, {"key": key})
