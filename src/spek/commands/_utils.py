from __future__ import annotations

import click


def read_text_arg(value: str) -> str:
    """Return stdin content if value is '-', otherwise return value unchanged."""
    if value == "-":
        return click.get_text_stream("stdin").read()
    return value
