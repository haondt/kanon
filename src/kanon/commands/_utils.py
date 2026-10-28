from __future__ import annotations

import json
from typing import NoReturn

import click

from kanon.core.config import KANON_BIN, KanonConfig

json_option = click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
input_json_option = click.option("--input-json", "input_json", is_flag=True, help="Parse text arguments as JSON strings")


def fail(error: Exception | str) -> NoReturn:
    """Print an error to stderr and exit 1."""
    click.echo(str(error.args[0] if isinstance(error, KeyError) else error), err=True)
    raise SystemExit(1)


def exit_ok(message: str) -> NoReturn:
    """Print a message to stdout and exit 0."""
    click.echo(message)
    raise SystemExit(0)


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
            fail(f"Invalid JSON input: {e}")
    return content


def kanon_command(subcommand: str) -> str:
    """Return the CLI invocation for a subcommand, including `-g` in global mode."""
    return f"{KANON_BIN} -g {subcommand}" if KanonConfig.is_global() else f"{KANON_BIN} {subcommand}"


def load_config_or_exit() -> KanonConfig:
    config = KanonConfig.get()
    if config is None:
        click.echo(f"No kanon.yaml found. Run '{kanon_command('init')}' first.")
        raise SystemExit(1)
    return config
