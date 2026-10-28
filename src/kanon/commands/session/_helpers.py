from __future__ import annotations

import json
from typing import Any

import click

from kanon.core.session import (
    SessionState,
    load_session,
    save_session,
    SESSION_FILE,
)
from kanon.commands._utils import fail, kanon_command


def load_session_or_exit() -> tuple[SessionState, str]:
    try:
        state, h = load_session()
    except FileNotFoundError:
        fail(f"{SESSION_FILE} not found. Run '{kanon_command('session')} start <goal>' first.")
    return state, h


def save_session_and_emit_hashes(state: SessionState, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = save_session(state)
    if as_json:
        payload: dict[str, Any] = {"before": before, "after": after}
        if extra:
            payload.update(extra)
        click.echo(json.dumps(payload))
    else:
        if extra:
            for k, v in extra.items():
                click.echo(f"{k}: {v}")
        click.echo(f"hash: {after}")
