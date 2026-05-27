from __future__ import annotations

import click

from spek.core.config import SpekConfig
from spek.core.sources import resolve_sources
from spek.commands.sync._synced import list_synced_stances, remove_synced_stance, write_synced_stance, create_synced_stances_dir

def sync_stances(pull: bool):
    config = SpekConfig.instance()
    create_synced_stances_dir()
    sources = resolve_sources()

    synced_stances = set(list_synced_stances())
    if pull:
        to_pull = set(config.stances_sr)
    else:
        to_pull = [s for s in config.stances_sr if s not in synced_stances]

    if pull:
        click.echo("Pulling stances from upstream:")
    if not to_pull:
        click.echo("No stance pulls required.")
    for resource in to_pull:
        stance = sources[resource.source].hydrate_stance(resource.path)
        write_synced_stance(resource, stance)
        click.echo(f"  stance:{resource.as_string} ← upstream")

    for resource in [s for s in synced_stances if s not in config.stances_sr]:
        remove_synced_stance(resource)
