from __future__ import annotations

import json as json_mod
from pathlib import Path

import click

from spek.core.plan import (
    PLANS_DIR,
    create_split,
    load_split_index,
)
from spek.commands._utils import read_text_arg


def _root(project_root: str) -> Path:
    return Path(project_root).resolve()


@click.group("split")
def split() -> None:
    """Manage plan splits (collections of related sub-plans)."""


@split.command("create")
@click.argument("name")
@click.argument("goal")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def split_create(name: str, goal: str, project_root: str, as_json: bool) -> None:
    """Create a new split with an index."""
    root = _root(project_root)
    try:
        index, h = create_split(read_text_arg(goal).strip(), root, name)
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json_mod.dumps({"hash": h, "goal": index.goal}))
    else:
        click.echo(f"Split created. hash: {h}")


@split.command("list")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def split_list(project_root: str, as_json: bool) -> None:
    """List all splits."""
    root = _root(project_root)
    plans_dir = root / PLANS_DIR
    results = []
    if plans_dir.exists():
        for d in sorted(plans_dir.iterdir()):
            if d.is_dir() and (d / "index.yaml").exists():
                try:
                    index, _ = load_split_index(root, d.name)
                    results.append({"name": d.name, "goal": index.goal})
                except Exception as e:
                    click.echo(f"Warning: could not load split {d.name!r}: {e}", err=True)
    if as_json:
        click.echo(json_mod.dumps(results))
    else:
        for r in results:
            click.echo(f"{r['name']}: {r['goal']}")


@split.command("status")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(file_okay=False))
@click.option("--json", "as_json", is_flag=True)
def split_status(name: str, project_root: str, as_json: bool) -> None:
    """Show a split's goal and each sub-plan's status."""
    root = _root(project_root)
    try:
        index, h = load_split_index(root, name)
    except FileNotFoundError:
        click.echo(f"Split {name!r} not found.", err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json_mod.dumps({
            "hash": h,
            "goal": index.goal,
            "plans": {k: v.model_dump() for k, v in index.plans.items()},
        }))
        return
    click.echo(f"goal: {index.goal}")
    for plan_name, entry in index.plans.items():
        click.echo(f"  {plan_name}: {entry.status}")
