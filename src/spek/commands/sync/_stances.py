from __future__ import annotations

import click

from spek.core.config import SpekConfig
from spek.commands.sync._synced import list_synced_stances, remove_synced_stance, write_synced_stance, create_synced_stances_dir
from spek.core.sources import SourceResolver

def sync_stances(pull: bool):
    config = SpekConfig.instance()
    create_synced_stances_dir()
    sources = SourceResolver.instance()

    synced_stances = set(list_synced_stances())
    dealiased_config_stances = [sources.dealias(r) for r in config.stances_sr]
    if pull:
        to_pull = dealiased_config_stances
    else:
        to_pull = [s for s in dealiased_config_stances if s not in synced_stances]

    if pull:
        click.echo("Pulling stances from upstream:")
    elif not to_pull:
        click.echo("No stance pulls required.")
    for resource in to_pull:
        source = sources.try_resolve(resource.source)
        if source is None:
            click.echo(f"Error: source '{resource.source}' not found for stance '{resource.as_string}'")
            raise SystemExit(1)
        stance = source.hydrate_stance(resource.path)
        write_synced_stance(resource, stance)
        click.echo(f"  stance:{resource.as_string} ← upstream")

    for resource in [s for s in synced_stances if s not in dealiased_config_stances]:
        remove_synced_stance(resource)
