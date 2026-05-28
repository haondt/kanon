from __future__ import annotations

import json as json_mod
from typing import Any

import click

from spek.core.todo import (
    TodoState,
    create_todo,
    load_todo,
    save_todo,
    TODO_FILE,
)


def load_todo_file(create: bool = False) -> tuple[TodoState, str]:
    try:
        state, h = load_todo()
    except FileNotFoundError:
        if create:
            state, h = create_todo()
        else:
            click.echo(f"{TODO_FILE} not found.", err=True)
            raise SystemExit(1)
    return state, h

def save_todo_file_and_emit_hashes(state: TodoState, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = save_todo(state)
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
