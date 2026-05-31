from __future__ import annotations

import json as json_mod
from pathlib import Path
from typing import Any

import click

from spek.core.plan import PlanFile, load_plan, save_plan


def _root(project_root: str) -> Path:
    return Path(project_root).resolve()


def _load(name: str, project_root: str) -> tuple[PlanFile, str, Path]:
    root = _root(project_root)
    try:
        plan, h = load_plan(root, name)
    except FileNotFoundError:
        click.echo(f"Plan {name!r} not found.", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    return plan, h, root


def _save_and_emit(plan: PlanFile, root: Path, name: str, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = save_plan(plan, root, name)
    if as_json:
        payload: dict[str, Any] = {"before": before, "after": after}
        if extra:
            payload.update(extra)
        click.echo(json_mod.dumps(payload))
    else:
        if extra:
            for k, v in extra.items():
                click.echo(f"{k}: {v}")
        click.echo(f"hash: {after}")
