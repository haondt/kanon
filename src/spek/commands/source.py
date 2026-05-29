from __future__ import annotations

import json
from typing import Any

import click

from spek.commands._utils import load_config_or_exit
from spek.core.config import SourceReference, SpekConfig, SpekEnv
from spek.core.settings import GlobalSettings
from spek.core.sources import AliasRef, LocalSource, hydrate_source_reference, resolve_sources
from spek.core.sources._base import PullResult

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
        source_name = SourceReference.parse(source_name, sanitize=True, validate_as_key=True).as_string
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)

    try:
        value = SourceReference.parse(path)
        hydrated = hydrate_source_reference(value)
        if isinstance(hydrated, AliasRef):
            resolved = resolve_sources().get(value)
            if resolved is None:
                raise ValueError(f"Unknown alias: {path!r}")
            hydrated = resolved
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)

    if global_scope:
        settings = GlobalSettings.instance()
        if source_name in settings.sources and not force:
            click.echo(f"Source '{source_name}' already exists. Use --force to overwrite.")
            raise SystemExit(1)
        settings.sources[source_name] = value.as_string
        settings.save()
        click.echo(f"Added source '{source_name}' to ~/.spek/settings.yaml.")
    else:
        config = load_config_or_exit()
        if source_name in config.sources and not force:
            click.echo(f"Source '{source_name}' already exists. Use --force to overwrite.")
            raise SystemExit(1)
        config.sources[source_name] = value.as_string
        config.save()
        click.echo(f"Added source '{source_name}' to spek.yaml.")

    pull_result = hydrated.pull()
    if pull_result == PullResult.CLONED:
        click.echo(f"Cached {value.as_fully_qualified_string}")


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
        click.echo(f"Removed source '{source_name}' from spek.yaml.")

@source.command("status")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON.")
@click.option("--global", "-g", "global_scope", is_flag=True, help="Show only global sources.")
def source_status(as_json: bool, global_scope: bool) -> None:
    """Show configured sources and their resolution status."""
    global_raw = GlobalSettings.instance().sources
    project_config = SpekConfig.get()
    project_raw = project_config.sources if project_config is not None else {}

    scope_map: dict[SourceReference, str] = {}
    for raw_key in global_raw:
        try:
            scope_map[SourceReference.parse(raw_key, validate_as_key=True)] = "global"
        except ValueError:
            pass
    for raw_key in project_raw:
        try:
            scope_map[SourceReference.parse(raw_key, validate_as_key=True)] = "project"
        except ValueError:
            pass

    resolved = resolve_sources()

    rows: list[Any] = []
    for source_key, source in resolved.items():
        scope = scope_map.get(source_key, "builtin")
        if global_scope and scope != "global":
            continue
        resolves = "no" if isinstance(source, LocalSource) and not source.root.exists() else "yes"
        rows.append({"name": source_key.as_string, "type": source_key.scheme, "scope": scope, "resolves": resolves, "path": source.serialize()})

    if as_json:
        click.echo(json.dumps(rows))
        return

    if not rows:
        click.echo("No sources configured.")
        return

    name_w = max(len(r["name"]) for r in rows)
    type_w = max(len(r["type"]) for r in rows)
    scope_w = max(len(r["scope"]) for r in rows)
    resolves_w = max(len(r["resolves"]) for r in rows)
    path_w = max(len(r["path"]) for r in rows)
    click.echo(f"  {'name':<{name_w}}  {'type':<{type_w}}  {'scope':<{scope_w}}  {'resolves':<{resolves_w}}  {'path':<{path_w}}")
    click.echo(f"  {'-' * name_w}  {'-' * type_w}  {'-' * scope_w}  {'-' * resolves_w}  {'-' * path_w}")
    for r in rows:
        click.echo(f"  {r['name']:<{name_w}}  {r['type']:<{type_w}}  {r['scope']:<{scope_w}}  {r['resolves']:<{resolves_w}}  {r['path']:<{path_w}}")


@source.command("pull")
@click.argument("name", required=False, default=None)
def source_pull(name: str | None) -> None:
    """Pull remote sources into the local cache.

    With no arguments, pulls all resolved sources (non-remote sources are skipped).
    With NAME, pulls only the named source (alias or direct reference like gh::org/repo).
    """
    resolved = resolve_sources()

    if name is None:
        for source_key, src in resolved.items():
            result = src.pull(force=True)
            if result != PullResult.NOOP:
                click.echo(f"{source_key.as_string} ← {result.value}")

    else:
        ref = SourceReference.parse(name, sanitize=True)
        if ref in resolved:
            src = resolved[ref]
        else:
            try:
                hydrated = hydrate_source_reference(ref)
                if isinstance(hydrated, AliasRef):
                    raise ValueError
                src = hydrated
            except ValueError:
                click.echo(f"Unknown source: {name!r}")
                raise SystemExit(1)
        result = src.pull(force=True)
        if result != PullResult.NOOP:
            click.echo(f"{ref.as_string} ← {result.value}")
