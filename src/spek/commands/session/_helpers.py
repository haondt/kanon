from __future__ import annotations

import json as json_mod
from pathlib import Path
from typing import Any

import click

from spek.core.session import (
    SessionState,
    load_session,
    save_session,
    SESSION_FILE,
)


def load_session_or_exit() -> tuple[SessionState, str]:
    try:
        state, h = load_session()
    except FileNotFoundError:
        click.echo(f"{SESSION_FILE} not found. Run 'spek session start <goal>' first.", err=True)
        raise SystemExit(1)
    return state, h


def save_session_and_emit_hashes(state: SessionState, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = save_session(state)
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
