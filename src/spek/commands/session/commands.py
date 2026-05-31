from __future__ import annotations

import json as json_mod
from typing import Any

import click

from spek.core.plan import (
    SplitEntry,
    load_plan,
    load_split_index,
    parse_plan_ref,
    save_split_index,
)
from spek.core.session import (
    SESSION_FILE,
    PlanStep,
    SessionState,
    create_session,
    delete_session,
    lint_session,
    save_session,
)
from ._helpers import _load, _root
from spek.commands._utils import read_text_arg


@click.command("start")
@click.argument("goal")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_start(goal: str, project_root: str, as_json: bool) -> None:
    """Create a new session with the given goal."""
    root = _root(project_root)
    try:
        state, h = create_session(read_text_arg(goal), root)
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "goal": state.goal}))
    else:
        click.echo(f"Session started. hash: {h}")


@click.command("goal")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_goal(project_root: str, as_json: bool) -> None:
    """Read the current session goal."""
    state, h, _ = _load(project_root)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "goal": state.goal}))
    else:
        click.echo(state.goal)


@click.command("status")
@click.option("--full", is_flag=True)
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_status(full: bool, project_root: str, as_json: bool) -> None:
    """Show session summary."""
    state, h, _ = _load(project_root)

    steps_total = len(state.plan.steps)
    steps_done = sum(1 for s in state.plan.steps.values() if s.done)
    passes = len(state.review)
    findings_open = sum(
        1 for rp in state.review.values()
        for f in rp.findings.values()
        if f.status in ("open", "reopened")
    )

    if as_json:
        payload: dict[str, Any] = {
            "hash": h,
            "goal": state.goal,
            "plan": {
                "steps_total": steps_total,
                "steps_done": steps_done,
                "notes_count": len(state.plan.notes),
            },
            "stance": state.stance,
            "build": {"notes_count": len(state.build.notes)},
            "review": {"passes": passes, "findings_open": findings_open},
            "amendments": len(state.amendments),
            "detours": len(state.detours),
        }
        if full:
            payload["plan"]["steps"] = {k: v.model_dump() for k, v in state.plan.steps.items()}
            payload["plan"]["notes"] = dict(state.plan.notes)
            payload["build"]["notes"] = dict(state.build.notes)
            payload["review_passes"] = {
                pk: {
                    "status": rp.status,
                    "findings": {fk: f.model_dump() for fk, f in rp.findings.items()},
                }
                for pk, rp in state.review.items()
            }
            payload["amendments"] = list(state.amendments)
            payload["detours"] = list(state.detours)
        click.echo(json_mod.dumps(payload))
        return

    click.echo(f"goal: {state.goal}")
    click.echo(f"plan: {steps_done}/{steps_total} steps done, {len(state.plan.notes)} note(s)")
    if state.stance:
        click.echo(f"stance: {state.stance}")
    click.echo(f"build: {len(state.build.notes)} note(s)")
    click.echo(f"review: {passes} pass(es), {findings_open} open finding(s)")
    click.echo(f"amendments: {len(state.amendments)}  detours: {len(state.detours)}")
    click.echo(f"hash: {h}")

    if full:
        if state.plan.steps:
            click.echo("\nPlan steps:")
            for k, s in state.plan.steps.items():
                mark = "✓" if s.done else " "
                click.echo(f"  [{mark}] {k}: {s.text}")
        if state.plan.notes:
            click.echo("\nPlan notes:")
            for k, n in state.plan.notes.items():
                click.echo(f"  {k}: {n}")
        if state.build.notes:
            click.echo("\nBuild notes:")
            for k, n in state.build.notes.items():
                click.echo(f"  {k}: {n}")
        if state.review:
            click.echo("\nReview:")
            for pk, rp in state.review.items():
                click.echo(f"  {pk} [{rp.status}]:")
                for fk, f in rp.findings.items():
                    click.echo(f"    {fk} [{f.status}] {f.type}/{f.severity}: {f.text}")
        if state.amendments:
            click.echo("\nAmendments:")
            for a in state.amendments:
                click.echo(f"  - {a}")
        if state.detours:
            click.echo("\nDetours:")
            for d in state.detours:
                click.echo(f"  - {d}")


@click.command("lint")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_lint(project_root: str, as_json: bool) -> None:
    """Lint the session file."""
    state, h, _ = _load(project_root)
    issues = lint_session(state)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "issues": issues}))
    else:
        if issues:
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("No issues found.")


@click.command("clear")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_clear(project_root: str, as_json: bool) -> None:
    """Delete the session file."""
    root = _root(project_root)
    try:
        delete_session(root)
    except FileNotFoundError:
        click.echo(f"{SESSION_FILE} not found.", err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json_mod.dumps({"cleared": True}))
    else:
        click.echo("Session cleared.")


@click.command("load")
@click.argument("path")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def session_load(path: str, project_root: str, as_json: bool) -> None:
    """Load a plan file into a new session."""
    root = _root(project_root)
    session_path = root / SESSION_FILE
    if session_path.exists():
        click.echo(f"{SESSION_FILE} already exists. Use 'spek session clear' first.", err=True)
        raise SystemExit(1)

    try:
        split, bare = parse_plan_ref(path)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    try:
        plan_obj, _ = load_plan(root, path)
    except FileNotFoundError:
        click.echo(f"Plan {path!r} not found.", err=True)
        raise SystemExit(1)

    state = SessionState(goal=plan_obj.goal)
    for k, s in plan_obj.steps.items():
        state.plan.steps[k] = PlanStep(text=s.text, done=False)
    state.plan.notes = dict(plan_obj.notes)
    state._meta.next_key = dict(plan_obj._meta.next_key)

    _, h = save_session(state, root)

    if split is not None:
        try:
            index, _ = load_split_index(root, split)
            if bare in index.plans and index.plans[bare].status != "done":
                index.plans[bare] = SplitEntry(status="in_progress")
                save_split_index(index, root, split)
        except FileNotFoundError:
            pass

    if as_json:
        click.echo(json_mod.dumps({"hash": h, "goal": state.goal}))
    else:
        click.echo(f"Session loaded from plan {path!r}. hash: {h}")
