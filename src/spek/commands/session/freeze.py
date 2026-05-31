from __future__ import annotations

import json as json_mod

import click

from spek.core.plan import (
    PlanFile, SplitEntry, create_plan, index_path, load_split_index,
    parse_plan_ref, save_plan, save_split_index,
)
from spek.core.session import SESSION_FILE, delete_session
from ._helpers import _load, _root


@click.command("freeze")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_freeze(name: str, project_root: str, as_json: bool) -> None:
    """Freeze the session plan into a plan file and delete the session."""
    state, _, root = _load(project_root)

    if not state.plan.steps:
        click.echo("Cannot freeze: session has no plan steps.", err=True)
        raise SystemExit(1)
    if state.build.notes:
        click.echo("Cannot freeze: build has already started (build notes present).", err=True)
        raise SystemExit(1)
    if any(s.done for s in state.plan.steps.values()):
        click.echo("Cannot freeze: one or more plan steps are already marked done.", err=True)
        raise SystemExit(1)

    try:
        split, bare = parse_plan_ref(name)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if split is not None:
        idx_path = index_path(root, split)
        if not idx_path.exists():
            click.echo(f"Split {split!r} does not exist.", err=True)
            raise SystemExit(1)

    try:
        plan_obj, h = create_plan(state.goal, root, name)
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    plan_obj.steps = dict(state.plan.steps)
    plan_obj.notes = dict(state.plan.notes)
    plan_obj._meta.next_key = dict(state._meta.next_key)
    _, h = save_plan(plan_obj, root, name)

    if split is not None:
        index, _ = load_split_index(root, split)
        if bare not in index.plans or index.plans[bare].status != "done":
            index.plans[bare] = SplitEntry(status="pending")
            save_split_index(index, root, split)

    delete_session(root)

    if as_json:
        click.echo(json_mod.dumps({"frozen": True, "plan": name, "hash": h}))
    else:
        click.echo(f"Session frozen to plan {name!r}. hash: {h}")
