from __future__ import annotations

import click

from spek.commands._utils import load_config_or_exit
from spek.commands.sync._modules import sync_modules
from spek.commands.sync._render import render_all
from spek.commands.sync._stances import sync_stances
from spek.commands.sync._synced import read_synced_stance
from spek.core.config import SourceReference, SpekConfig
from spek.core.sources import resolve_sources


def do_sync(pull: bool = False) -> None:
    """Core sync logic — callable programmatically from other commands."""
    load_config_or_exit()

    sync_stances(pull)
    config = SpekConfig.instance()
    explicit_modules = set(config.modules_sr)
    all_modules_needed = set(explicit_modules)
    for res in config.stances_sr:
        all_modules_needed = all_modules_needed | set(read_synced_stance(res).modules_sr)

    sources = resolve_sources()

    if pull:
        needed_refs = {sr.source for sr in all_modules_needed}
        for ref, src in sources.items():
            if ref in needed_refs:
                src.pull(force=True)

        spek_source = sources[SourceReference.SPEK_SOURCE_REFERENCE]
        new_sha = spek_source.get_sha()
        click.echo(f"Recording SHA {new_sha[:8]}.")
        config.meta.spek_sha = new_sha
        config.save()

    sync_modules(all_modules_needed, pull)
    render_all(explicit_modules)
    click.echo("Done.")


@click.command()
@click.option("--pull", is_flag=True,
              help="Force-refresh all stances and modules from the upstream spek repo and record SHA.")
def sync(pull: bool) -> None:
    """Sync spec modules and stances, then generate AI tool output.

    Reads from .spek/modules/ and .spek/stances/ (local committed copies).
    Missing files are pulled from the upstream spek repo automatically.
    Use --pull to force-refresh everything from the spek repo and record SHA.
    Only modules listed in spek.yaml.modules become rules/commands.
    Modules referenced only by stances stay in .spek/modules/ and are inert
    until activated via /spek-stance.
    """
    do_sync(pull=pull)
