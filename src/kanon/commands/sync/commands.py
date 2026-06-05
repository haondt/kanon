from __future__ import annotations

import click

from kanon.commands._utils import load_config_or_exit
from kanon.commands.sync._kanons import sync_kanons
from kanon.commands.sync._render import render_all
from kanon.commands.sync._stances import sync_stances
from kanon.commands.sync._synced import read_synced_stance
from kanon.core.config import SourceReference, KanonConfig, SourcedResource
from kanon.core.sources import SourceResolver


def do_sync(pull: bool = False) -> None:
    """Core sync logic — callable programmatically from other commands."""
    load_config_or_exit()

    sync_stances(pull)
    config = KanonConfig.instance()
    sources = SourceResolver.instance()
    explicit_kanons = {sources.dealias(r) for r in config.kanons_sr}
    all_kanons_needed = set(explicit_kanons)
    for res in config.stances_sr:
        for r in read_synced_stance(res).kanons_sr:
            if r.source == SourceReference.SELF_SOURCE_REFERENCE:
                r = SourcedResource(source=res.source, path=r.path, args=r.args)
            all_kanons_needed = all_kanons_needed | {sources.dealias(r)}


    if pull:
        needed_refs = {sr.source for sr in all_kanons_needed}
        for ref in needed_refs:
            if ref == SourceReference.SELF_SOURCE_REFERENCE:
                continue
            sources[ref].pull(force=True)

        kanon_source = sources[SourceReference.KANON_SOURCE_REFERENCE]
        new_sha = kanon_source.get_sha()
        click.echo(f"Recording SHA {new_sha[:8]}.")
        config.meta.kanon_sha = new_sha
        config.save()

    sync_kanons(all_kanons_needed, pull)
    render_all(explicit_kanons)
    click.echo("Done.")


@click.command()
@click.option("--pull", is_flag=True,
              help="Force-refresh all stances and kanons from the upstream kanon repo and record SHA.")
def sync(pull: bool) -> None:
    """Sync kanons and stances, then generate AI tool output.

    Reads from .kanon/kanons/ and .kanon/stances/ (local committed copies).
    Missing files are pulled from the upstream kanon repo automatically.
    Use --pull to force-refresh everything from the kanon repo and record SHA.
    Only kanons listed in kanon.yaml.kanons become rules/commands.
    Kanons referenced only by stances stay in .kanon/kanons/ and are inert
    until activated via /kanon-stance.
    """
    do_sync(pull=pull)
