from __future__ import annotations

import click

from kanon.commands.sync._synced import list_synced_kanons, remove_synced_kanon, write_synced_kanon, create_synced_kanons_dir
from kanon.core.config import SourcedResource
from kanon.core.sources import SourceResolver

def sync_kanons(all_kanons_needed: set[SourcedResource], pull: bool):
    create_synced_kanons_dir()
    sources = SourceResolver.instance()

    synced_kanons = list_synced_kanons()
    all_kanons_needed = {sources.dealias(r) for r in all_kanons_needed}
    synced_paths = {s.as_path_string for s in synced_kanons}
    needed_paths = {r.as_path_string for r in all_kanons_needed}

    if pull:
        to_pull = list(all_kanons_needed)
    else:
        to_pull = [s for s in all_kanons_needed if s.as_path_string not in synced_paths]

    if pull:
        click.echo("Pulling kanons from upstream:")
    elif not to_pull:
        click.echo("No kanon pulls required.")

    for resource in to_pull:
        source = sources.try_resolve(resource.source)
        if source is None:
            click.echo(f"Error: source '{resource.source}' not found for kanon '{resource.as_string}'")
            raise SystemExit(1)
        kanon = source.hydrate_kanon(resource.path)
        write_synced_kanon(resource, kanon)
        click.echo(f"  kanon:{resource.as_string} ← upstream")

    for resource in [s for s in synced_kanons if s.as_path_string not in needed_paths]:
        remove_synced_kanon(resource)
