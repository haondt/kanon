from __future__ import annotations

import json

import click
import questionary
from questionary import Choice

from kanon.commands._utils import load_config_or_exit
from kanon.core.config import SourceReference, SourcedResource, KanonConfig
from kanon.core.sources import SourceResolver


def _pull_sources_for_kanons(kanon_strings: list[str]) -> None:
    pulled: set[SourceReference] = set()
    for m in kanon_strings:
        sr = SourcedResource.parse(m)
        src = sr.source
        if src not in pulled:
            pulled.add(src)
            SourceResolver.instance()[src].pull()


def _all_available() -> list[SourcedResource]:
    result: list[SourcedResource] = []
    for source_ref, source in SourceResolver.instance().items():
        for path in source.list_kanons():
            result.append(SourcedResource(source_ref, path))
    return sorted(result, key=lambda f: f.as_fully_qualified_string)


@click.command("edit")
@click.option("--sync", "run_sync", is_flag=True, help="Run kanon sync after saving.")
def edit(run_sync: bool) -> None:
    """Interactively select kanons."""
    _do_picker(run_sync)


def _do_picker(run_sync: bool) -> None:
    config = load_config_or_exit()
    sources = SourceResolver.instance()

    available = _all_available()
    available = { m.as_string: sources[m.source].hydrate_kanon(m.path) for m in available }

    selected_set = set(SourcedResource.sanitize(config.kanons))
    choices = [
        Choice(
            title=name,
            checked=(name in selected_set),
            description=m.description,
        )
        for name, m in available.items()
    ]

    result = questionary.checkbox(
        "Select kanons:",
        choices=choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if result is None:
        click.echo("No kanons selected. Aborting.")
        raise SystemExit(1)

    config.kanons = result
    config.save()
    click.echo(f"Saved {len(result)} kanon(s) to kanon.yaml.")

    _pull_sources_for_kanons(result)

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to update AI tool output.")


@click.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def list_cmd(as_json: bool) -> None:
    """List all available kanons with descriptions."""
    config = load_config_or_exit()
    selected_set = set(SourcedResource.sanitize(config.kanons))
    sources = SourceResolver.instance()
    available = _all_available()
    available = { m.as_string: (m, sources[m.source].hydrate_kanon(m.path)) for m in available }

    if as_json:
        results = [
            {
                "name": name,
                "description": m[1].description,
                "active": name in selected_set,
                "source": m[0].source.as_string,
            }
            for name, m in available.items()
        ]
        click.echo(json.dumps(results))
        return

    if not available:
        return

    width = max(len(name) for name in available)
    for name, m in available.items():
        desc = m[1].description
        marker = "✓" if name in selected_set else " "
        label = f"[{m[0].source.as_string}] " if m[0].source != SourceReference.KANON_SOURCE_REFERENCE else ""
        click.echo(f"  [{marker}] {name:<{width}}  {label}{desc}")


@click.command("set")
@click.argument("kanons", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run kanon sync after saving.")
def set_cmd(kanons: tuple[str, ...], run_sync: bool) -> None:
    """Non-interactively set the kanon list (full replacement)."""
    kanon_refs = [SourcedResource.parse(r) for r in SourcedResource.sanitize(kanons)]
    config = load_config_or_exit()
    sources = SourceResolver.instance()
    unknown = [m.as_string for m in kanon_refs if sources.try_resolve(m.source) is None or not sources[m.source].contains_kanon(m.path)]
    if unknown:
        click.echo(f"Unknown kanon(s): {', '.join(unknown)}")
        raise SystemExit(1)

    config.kanons = [r.as_string for r in kanon_refs]
    config.save()
    click.echo(f"Saved {len(kanons)} kanon(s) to kanon.yaml.")

    _pull_sources_for_kanons([r.as_string for r in kanon_refs])

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to update AI tool output.")


@click.command("add")
@click.argument("kanons", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run kanon sync after saving.")
def add(kanons: tuple[str, ...], run_sync: bool) -> None:
    """Append kanons to kanon.yaml."""
    kanons_sanitized = SourcedResource.sanitize(kanons)
    kanon_refs = [SourcedResource.parse(r) for r in kanons_sanitized]
    config = load_config_or_exit()
    sources = SourceResolver.instance()
    unknown = [m.as_string for m in kanon_refs if sources.try_resolve(m.source) is None or not sources[m.source].contains_kanon(m.path)]
    if unknown:
        click.echo(f"Unknown kanon(s): {', '.join(unknown)}")
        raise SystemExit(1)

    selected_set = set(SourcedResource.sanitize(config.kanons))
    already_active = [m for m in kanons_sanitized if m in selected_set]
    if already_active:
        click.echo(f"{', '.join(already_active)} already active.")

    new_kanons = SourcedResource.sanitize(kanons_sanitized + list(selected_set))
    config.kanons = new_kanons
    config.save()
    click.echo(f"Added {len(kanons)} kanon(s) to kanon.yaml.")

    _pull_sources_for_kanons(new_kanons)

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to update AI tool output.")


@click.command("remove")
@click.argument("kanons", nargs=-1, required=True)
@click.option("--sync", "run_sync", is_flag=True, help="Run kanon sync after saving.")
def remove(kanons: tuple[str, ...], run_sync: bool) -> None:
    """Remove kanons from kanon.yaml."""
    kanons_sanitized = SourcedResource.sanitize(kanons)
    config = load_config_or_exit()

    active_sanitized = SourcedResource.sanitize(config.kanons)
    active_set = set(active_sanitized)
    to_deactivate = [m for m in kanons_sanitized if m in active_set]
    if not to_deactivate:
        click.echo("All kanons already inactive")
        raise SystemExit(0)

    config.kanons = [m for m in active_sanitized if m not in to_deactivate]
    config.save()
    click.echo(f"Removed {len(kanons)} kanon(s) from kanon.yaml.")

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to update AI tool output.")


@click.command("search")
@click.argument("terms", nargs=-1, required=True)
@click.option("--source", "source_filter", default=None, help="Filter to a specific source by name.")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def search(terms: tuple[str, ...], source_filter: str | None, as_json: bool) -> None:
    """Search available kanons by name and description.

    All terms must match (case-insensitive). Unlike 'kanon ref search', this
    searches kanon names and descriptions in the kanon library, not reference
    entries.
    """
    config = KanonConfig.get()
    active_sanitized = set()
    sources = SourceResolver.instance()
    if config is not None:
        active_sanitized = set(SourcedResource.sanitize(config.kanons))

    parsed_source_filter: SourceReference | None = None
    if source_filter:
        parsed_source_filter = SourceReference.parse(source_filter)

    if parsed_source_filter and sources.try_resolve(parsed_source_filter) is None:
        click.echo(f"Unknown source: '{source_filter}'")
        raise SystemExit(1)

    available = _all_available()
    lower_terms = [t.lower() for t in terms]

    results: list[tuple[str, SourceReference, str]] = []
    for ref in available:
        if parsed_source_filter and ref.source != parsed_source_filter:
            continue
        desc = sources[ref.source].hydrate_kanon(ref.path).description or ""
        haystack = f"{ref.as_string} {desc}".lower()
        if all(t in haystack for t in lower_terms):
            results.append((ref.as_string, ref.source, desc))

    if as_json:
        click.echo(json.dumps([
            {"name": name, "description": desc, "active": name in active_sanitized, "source": source_key.as_string}
            for name, source_key, desc in results
        ]))
        return

    if not results:
        return

    width = max(len(name) for name, _, _ in results)
    for name, source_key, desc in results:
        marker = "✓" if name in active_sanitized else " "
        label = f"[{source_key.as_string}] " if source_key != SourceReference.KANON_SOURCE_REFERENCE else ""
        click.echo(f"  [{marker}] {name:<{width}}  {label}{desc}")
