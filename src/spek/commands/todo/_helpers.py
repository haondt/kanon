from __future__ import annotations

import json as json_mod
from pathlib import Path
from typing import Any

import click

from spek.core.todo import (
    TodoState,
    create_todo,
    load_todo,
    save_todo,
    TODO_FILE,
)


def _root(project_root: str) -> Path:
    return Path(project_root).resolve()


def _load(project_root: str) -> tuple[TodoState, str, Path]:
    root = _root(project_root)
    try:
        state, h = load_todo(root)
    except FileNotFoundError:
        click.echo(f"{TODO_FILE} not found.", err=True)
        raise SystemExit(1)
    return state, h, root


def _load_or_create(project_root: str) -> tuple[TodoState, str, Path]:
    """Load todo.yaml, creating an empty one if it doesn't exist."""
    root = _root(project_root)
    try:
        state, h = load_todo(root)
    except FileNotFoundError:
        state, h = create_todo(root)
    return state, h, root


def _save_and_emit(state: TodoState, root: Path, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = save_todo(state, root)
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
