from __future__ import annotations

import json
from typing import Any

import click

from kanon.core.table import TableState


def save_table_file_and_emit_hashes(state: TableState, as_json: bool, extra: dict[str, Any] | None = None) -> None:
    before, after = state.save()
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


def emit_no_change(message: str, as_json: bool, hash_: str, extra: dict[str, Any] | None = None) -> None:
    if as_json:
        click.echo(json.dumps({"hash": hash_, "existed": True, **(extra or {})}))
    else:
        click.echo(message)
        click.echo(f"hash: {hash_}")
