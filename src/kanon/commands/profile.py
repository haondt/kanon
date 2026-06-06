from __future__ import annotations

import json

import click

from kanon.commands._utils import load_config_or_exit
from kanon.core.config import SourceReference, SourcedResource
from kanon.core.sources import SourceResolver


@click.group()
def profile() -> None:
    """Inspect and apply profiles."""


@profile.command("list")
def profile_list() -> None:
    """List all available profiles."""
    load_config_or_exit()
    sources = SourceResolver.instance()
    profile_refs: list[SourcedResource] = []
    for source_key, source in sources.items():
        for path in source.list_profiles():
            profile_refs.append(SourcedResource(source_key, path))
    profile_refs = sorted(profile_refs, key=lambda f: f.as_fully_qualified_string)
    profiles = { r.as_string: sources[r.source].shallow_hydrate_profile(r.path) for r in profile_refs }

    if not profiles:
        click.echo("No profiles found.")
        return
    width = max(len(k) for k in profiles.keys())
    for k, v in profiles.items():
        click.echo(f"  {k:<{width}}  {v.description}")


@profile.command("apply")
@click.argument("name", required=False)
@click.option("--sync", "run_sync", is_flag=True,
              help="Run kanon sync after applying the profile.")
@click.option("--replace", "-r", "replace", is_flag=True,
              help="Replace existing kanons/stances instead of merging.")
def profile_apply(name: str | None, run_sync: bool, replace: bool) -> None:
    """Re-resolve a profile and update kanons in kanon.yaml.

    Uses the profile recorded in kanon.yaml if NAME is omitted.
    By default, merges profile kanons/stances with existing ones.
    Use --replace to discard existing kanons/stances and use only the profile.
    """
    config = load_config_or_exit()
    profile_ref = name or config.meta.profile

    if not profile_ref:
        click.echo("No profile recorded in kanon.yaml and no NAME given.")
        raise SystemExit(1)

    try:
        profile_ref = SourcedResource.parse(profile_ref)
        profile = SourceResolver.instance()[profile_ref.source].hydrate_profile(profile_ref)
    except FileNotFoundError as e:
        click.echo(str(e))
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)

    if replace:
        config.kanons = profile.kanons
        config.stances = profile.stances
        config.meta.profile = profile_ref.as_string
        config.save()
        click.echo(f"Applied profile '{profile_ref.as_string}': {len(config.kanons)} kanon(s), {len(config.stances)} stance(s) written to kanon.yaml.")
    else:
        existing_kanons = list(config.kanons)
        existing_stances = list(config.stances)
        merged_kanons = SourcedResource.sanitize(profile.kanons + existing_kanons)
        merged_stances = SourceReference.sanitize(profile.stances + existing_stances)
        added_kanons = len(merged_kanons) - len(SourcedResource.sanitize(existing_kanons))
        added_stances = len(merged_stances) - len(SourceReference.sanitize(existing_stances))
        config.kanons = merged_kanons
        config.stances = merged_stances
        config.meta.profile = profile_ref.as_string
        config.save()
        click.echo(f"Applied profile '{profile_ref.as_string}': added {added_kanons} kanon(s), {added_stances} stance(s) ({len(config.kanons)} total).")

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to update AI tool output.")


@profile.command("search")
@click.argument("terms", nargs=-1, required=True)
@click.option("--source", "source_filter", default=None, help="Filter to a specific source by name.")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def profile_search(terms: tuple[str, ...], source_filter: str | None, as_json: bool) -> None:
    """Search available profiles by name and description.

    All terms must match (case-insensitive).
    """
    load_config_or_exit()
    sources = SourceResolver.instance()

    parsed_source_filter: SourceReference | None = None
    if source_filter:
        parsed_source_filter = SourceReference.parse(source_filter)
        if sources.try_resolve(parsed_source_filter) is None:
            click.echo(f"Unknown source: '{source_filter}'")
            raise SystemExit(1)

    profile_refs: list[SourcedResource] = []
    for source_key, source in sources.items():
        if parsed_source_filter and source_key != parsed_source_filter:
            continue
        for path in source.list_profiles():
            profile_refs.append(SourcedResource(source_key, path))
    profile_refs = sorted(profile_refs, key=lambda f: f.as_fully_qualified_string)

    lower_terms = [t.lower() for t in terms]
    results: list[tuple[str, str]] = []
    for ref in profile_refs:
        desc = sources[ref.source].shallow_hydrate_profile(ref.path).description or ""
        haystack = f"{ref.as_string} {desc}".lower()
        if all(t in haystack for t in lower_terms):
            results.append((ref.as_string, desc))

    if as_json:
        click.echo(json.dumps([{"name": name, "description": desc} for name, desc in results]))
        return

    if not results:
        return

    width = max(len(name) for name, _ in results)
    for name, desc in results:
        click.echo(f"  {name:<{width}}  {desc}")
