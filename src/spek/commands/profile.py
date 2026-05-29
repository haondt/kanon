from __future__ import annotations

import click

from spek.commands._utils import load_config_or_exit
from spek.core.config import SourcedResource
from spek.core.sources import SourceResolver


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
              help="Run spek sync after applying the profile.")
def profile_apply(name: str | None, run_sync: bool) -> None:
    """Re-resolve a profile and update modules in spek.yaml.

    Uses the profile recorded in spek.yaml if NAME is omitted.
    """
    config = load_config_or_exit()
    profile_ref = name or config.meta.profile

    if not profile_ref:
        click.echo("No profile recorded in spek.yaml and no NAME given.")
        raise SystemExit(1)

    try:
        profile_ref = SourcedResource.parse(profile_ref)
        profile = SourceResolver.instance()[profile_ref.source].hydrate_profile(profile_ref.path)
    except FileNotFoundError as e:
        click.echo(str(e))
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)

    config.modules = profile.modules
    config.stances = profile.stances
    config.meta.profile = profile_ref.as_string
    config.save()
    click.echo(f"Applied profile '{profile_ref.as_string}': {len(config.modules)} module(s), {len(config.stances)} stance(s) written to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to update AI tool output.")
