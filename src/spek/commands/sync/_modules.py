from __future__ import annotations

import click

from spek.commands.sync._synced import list_synced_modules, remove_synced_module, write_synced_module, create_synced_modules_dir
from spek.core.config import SourcedResource
from spek.core.sources import SourceResolver

def sync_modules(all_modules_needed: set[SourcedResource], pull: bool):
    create_synced_modules_dir()
    sources = SourceResolver.instance()

    synced_modules = set(list_synced_modules())
    all_modules_needed = {sources.dealias(r) for r in all_modules_needed}
    if pull:
        to_pull = [s for s in all_modules_needed]
    else:
        to_pull = [s for s in all_modules_needed if s not in synced_modules]

    if pull:
        click.echo("Pulling modules from upstream:")
    elif not to_pull:
        click.echo("No module pulls required.")

    for resource in to_pull:
        source = sources.try_resolve(resource.source)
        if source is None:
            click.echo(f"Error: source '{resource.source}' not found for module '{resource.as_string}'")
            raise SystemExit(1)
        module = source.hydrate_module(resource.path)
        write_synced_module(resource, module)
        click.echo(f"  module:{resource.as_string} ← upstream")

    for resource in [s for s in synced_modules if s not in all_modules_needed]:
        remove_synced_module(resource)
