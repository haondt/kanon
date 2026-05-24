from __future__ import annotations

import json

import click


def read_text_arg(value: str) -> str:
    """Return stdin content if value is '-', otherwise return value unchanged."""
    if value == "-":
        return click.get_text_stream("stdin").read()
    return value


def read_text_arg_json(value: str, as_json: bool) -> str:
    """Return stdin content if value is '-', otherwise parse as JSON if as_json is True."""
    content = read_text_arg(value)
    if as_json:
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, str):
                raise ValueError("JSON input must be a string")
            return parsed
        except json.JSONDecodeError as e:
            click.echo(f"Invalid JSON input: {e}", err=True)
            raise SystemExit(1)
    return content
