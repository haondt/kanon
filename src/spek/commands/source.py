from __future__ import annotations

import json
from pathlib import Path

import click

from spek.commands._utils import load_config_or_exit
from spek.core.config import SpekEnv
from spek.core.settings import GlobalSettings
from spek.core.sources import parse_source_ref, resolve_sources

@click.group()
def source() -> None:
    """Manage named source directories for spec modules."""

@source.command("add")
@click.argument("source_name")
@click.argument("path")
@click.option("--global", "-g", "global_scope", is_flag=True, help="Write to ~/.spek/settings.yaml instead of spek.yaml.")
@click.option("--force", is_flag=True, help="Overwrite an existing source with the same name.")
def source_add(source_name: str, path: str, global_scope: bool, force: bool) -> None:
    """Add a named source.

    PATH may be a local path (/abs/path, ~/path) or a remote shorthand
    (gh::org/repo[@ref], gl::group/.../repo[@ref]).
    Local paths are expanded to absolute at add time.
    """
    try:
        parsed = parse_source_ref(path)
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)


    if global_scope:
        settings = GlobalSettings.instance()
        if source_name in settings.sources and not force:
            click.echo(f"Source '{source_name}' already exists. Use --force to overwrite.")
            raise SystemExit(1)
        settings.sources[source_name] = parsed.serialize()
        settings.save()
        click.echo(f"Added source '{source_name}' to ~/.spek/settings.yaml.")
    else:
        config = load_config_or_exit()
        if source_name in config.sources and not force:
            click.echo(f"Source '{source_name}' already exists. Use --force to overwrite.")
            raise SystemExit(1)
        config.sources[source_name] = parsed.serialize()
        config.save()
        click.echo(f"Added source '{source_name}' to spek.yaml.")


@source.command("remove")
@click.argument("source_name")
@click.option("--global", "-g", "global_scope", is_flag=True, help="Remove from global settings.")
def source_remove(source_name: str, global_scope: bool) -> None:
    """Remove a named source."""
    if global_scope:
        settings = GlobalSettings.instance()
        if source_name in settings.sources:
            del settings.sources[source_name]
            settings.save()
        click.echo(f"Removed source '{source_name}' from {SpekEnv.instance().settings_path}.")
    else:
        config = load_config_or_exit()
        if source_name in config.sources:
            del config.sources[source_name]
            config.save()
        click.echo(f"Removed source '{source_name}' from .")

@source.command("status")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON.")
def source_status(as_json: bool) -> None:
    """Show configured sources and their resolution status."""
    sources = resolve_sources()
    sources = { k: v.serialize() for k, v in sources.items() }

    if as_json:
        click.echo(json.dumps([{"name": k, "path": v} for k, v in sources.items()]))
        return

    if not sources:
        click.echo("No sources configured.")
        return

    name_w = max(len(k) for k in sources.keys())
    path_w = max(len(v) for v in sources.values())
    click.echo(f"  {'name':<{name_w}}  {'path':<{path_w}}")
    click.echo(f"  {'-' * name_w}  {'-' * path_w}")
    for k, v in sources.items():
        click.echo(f"  {k:<{name_w}}  {v:<{path_w}}")
