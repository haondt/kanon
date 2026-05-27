from __future__ import annotations

import json

import click

from spek.core.config import SpekConfig

def read_text_arg(value: str) -> str:
    """Return stdin content if value is '-', otherwise return value unchanged."""
    stripped_value = value.strip()
    if stripped_value == "-":
        return click.get_text_stream("stdin").read().strip()
    return stripped_value


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


def load_config_or_exit() -> SpekConfig:
    config = SpekConfig.get()
    if config is None:
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)
    return config
