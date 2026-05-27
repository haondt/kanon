from __future__ import annotations

import json as json_mod

import click
import questionary
from questionary import Choice

from spek.commands._utils import load_config_or_exit
from spek.core.config import SPEK_SOURCE, SourcedResource, SpekConfig
from spek.core.sources import resolve_sources

def _all_available() -> list[SourcedResource]:
    result: list[SourcedResource] = []
    for source_name, source in resolve_sources().items():
        for path in source.list_modules():
            result.append(SourcedResource(source_name, path))
    return sorted(result, key=lambda f: f.as_fully_qualified_string)

@click.group()
def module() -> None:
    """Manage modules in spek.yaml."""


@module.command("edit")
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_edit(run_sync: bool) -> None:
    """Interactively select modules."""
    _do_picker(run_sync)


def _do_picker(run_sync: bool) -> None:
    config = load_config_or_exit()
    sources = resolve_sources()

    available = _all_available()
    available = { m.as_string: sources[m.source].hydrate_module(m.path) for m in available }

    selected_set = set(SourcedResource.sanitize(config.modules))
    choices = [
        Choice(
            title=name,
            checked=(name in selected_set),
            description=m.description,
        )
        for name, m in available.items()
    ]

    result = questionary.checkbox(
        "Select modules:",
        choices=choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if not result:
        click.echo("No modules selected. Aborting.")
        raise SystemExit(1)

    config.modules = result
    config.save()
    click.echo(f"Saved {len(result)} module(s) to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to update AI tool output.")

@module.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def module_list(as_json: bool) -> None:
    """List all available modules with descriptions."""
    config = load_config_or_exit()
    selected_set = set(SourcedResource.sanitize(config.modules))
    sources = resolve_sources()
    available = _all_available()
    available = { m.as_string: (m, sources[m.source].hydrate_module(m.path)) for m in available }

    if as_json:
        results = [
            {
                "name": name,
                "description": m[1].description,
                "active": name in selected_set,
                "source": m[0].source,
            }
            for name, m in available.items()
        ]
        click.echo(json_mod.dumps(results))
        return

    if not available:
        return

    width = max(len(name) for name in available)
    for name, m in available.items():
        desc = m[1].description
        marker = "✓" if name in selected_set else " "
        label = f"[{m[0].source}] " if m[0].source != SPEK_SOURCE else ""
        click.echo(f"  [{marker}] {name:<{width}}  {label}{desc}")


@module.command("set")
@click.argument("modules", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_set(modules: tuple[str, ...], run_sync: bool) -> None:
    """Non-interactively set the module list (full replacement)."""
    module_refs = [SourcedResource.parse(r) for r in SourcedResource.sanitize(modules)]
    config = load_config_or_exit()
    sources = resolve_sources()
    unknown = [m.as_string for m in module_refs if m.source not in sources or not sources[m.source].contains_module(m.path)]
    if unknown:
        click.echo(f"Unknown module(s): {', '.join(unknown)}")
        raise SystemExit(1)

    config.modules = [r.as_string for r in module_refs]
    config.save()
    click.echo(f"Saved {len(modules)} module(s) to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to update AI tool output.")


@module.command("add")
@click.argument("modules", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_add(modules: tuple[str, ...], run_sync: bool) -> None:
    """Append modules to spek.yaml."""
    modules_sanitized = SourcedResource.sanitize(modules)
    module_refs = [SourcedResource.parse(r) for r in modules_sanitized]
    config = load_config_or_exit()
    sources = resolve_sources()
    unknown = [m.as_string for m in module_refs if m.source not in sources or not sources[m.source].contains_module(m.path)]
    if unknown:
        click.echo(f"Unknown module(s): {', '.join(unknown)}")
        raise SystemExit(1)

    selected_set = set(SourcedResource.sanitize(config.modules))
    already_active = [m for m in modules_sanitized if m in selected_set]
    if already_active:
        click.echo(f"{', '.join(already_active)} already active.")

    config.modules = SourcedResource.sanitize(modules_sanitized + list(selected_set))
    config.save()
    click.echo(f"Added {len(modules)} module(s) to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to update AI tool output.")


@module.command("remove")
@click.argument("modules", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_remove(modules: tuple[str, ...], run_sync: bool) -> None:
    """Remove modules from spek.yaml."""
    modules_sanitized = SourcedResource.sanitize(modules)
    config = load_config_or_exit()

    active_sanitized = SourcedResource.sanitize(config.modules)
    active_set = set(active_sanitized)
    to_deactivate = [m for m in modules_sanitized if m in active_set]
    if not to_deactivate:
        click.echo("All modules already inactive")
        raise SystemExit(0)

    config.modules = [m for m in active_sanitized if m not in to_deactivate]
    config.save()
    click.echo(f"Removed {len(modules)} module(s) from spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to update AI tool output.")


@module.command("search")
@click.argument("terms", nargs=-1, required=True)
@click.option("--source", "source_filter", default=None, help="Filter to a specific source by name.")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def module_search(terms: tuple[str, ...], source_filter: str | None, as_json: bool) -> None:
    """Search available modules by name and description.

    All terms must match (case-insensitive). Unlike 'spek ref search', this
    searches module names and descriptions in the spec library, not reference
    entries.
    """
    config = SpekConfig.get()
    active_sanitized = set()
    sources = resolve_sources()
    if config is not None:
        active_sanitized = set(SourcedResource.sanitize(config.modules))

    if source_filter and source_filter not in sources:
        click.echo(f"Unknown source: '{source_filter}'")
        raise SystemExit(1)

    available = _all_available()
    lower_terms = [t.lower() for t in terms]

    results: list[tuple[str, str, str]] = []
    for ref in available:
        if source_filter and ref.source != source_filter:
            continue
        desc = sources[ref.source].hydrate_module(ref.path).description or ""
        haystack = f"{ref.as_string} {desc}".lower()
        if all(t in haystack for t in lower_terms):
            results.append((ref.as_string, ref.source, desc))

    if as_json:
        click.echo(json_mod.dumps([
            {"name": name, "description": desc, "active": name in active_sanitized, "source": source}
            for name, source, desc in results
        ]))
        return

    if not results:
        return

    width = max(len(name) for name, _, _ in results)
    for name, ns, desc in results:
        marker = "✓" if name in active_sanitized else " "
        label = f"[{ns}] " if ns != "spek" else ""
        click.echo(f"  [{marker}] {name:<{width}}  {label}{desc}")
