from __future__ import annotations

import click

from kanon.commands._utils import load_config_or_exit
from kanon.core.config import SourceReference, SourcedResource
from kanon.core.settings import GlobalSettings
from kanon.core.sources import GitHubSource, GitLabSource, LocalSource, SourceResolver, hydrate_source_reference, AliasRef


@click.command("check")
def check() -> None:
    """Check that all configured kanons, stances, and sources are valid."""
    config = load_config_or_exit()
    global_settings = GlobalSettings.instance()

    errors: list[str] = []
    infos: list[str] = []

    for sources_dict in (global_settings.sources, config.sources):
        for label, path in sources_dict.items():
            try:
                parsed = hydrate_source_reference(SourceReference.parse(path))
            except ValueError as e:
                errors.append(f"Invalid source path for {label}: {e}")
                continue
            if isinstance(parsed, AliasRef):
                pass
            elif isinstance(parsed, LocalSource):
                if not parsed.root.exists():
                    errors.append(f"Source {label!r} path does not exist: {parsed.root}")
            elif isinstance(parsed, (GitHubSource, GitLabSource)):
                infos.append(f"Source {label!r} is a remote source (not yet fetched): {path}")

    sources = SourceResolver.instance()

    for kanon_ref in config.kanons:
        kanon = SourcedResource.parse(kanon_ref)
        if (resolved := sources.try_resolve(kanon.source)) is None:
            errors.append(f"Could not resolve kanon {kanon_ref!r} because the source does not exist.")
        elif not resolved.contains_kanon(kanon.path):
            source_obj = sources[kanon.source]
            if isinstance(source_obj, (GitHubSource, GitLabSource)):
                infos.append(f"Kanon entry {kanon_ref!r} references a remote source (not yet fetched).")
            else:
                errors.append(f"Could not resolve kanon {kanon_ref!r} because the source does not contain it.")

    for stance_ref in config.stances:
        stance = SourcedResource.parse(stance_ref)
        if (resolved := sources.try_resolve(stance.source)) is None:
            errors.append(f"Could not resolve stance {stance_ref!r} because the source does not exist.")
        elif not sources[stance.source].contains_stance(stance.path):
            source_obj = sources[stance.source]
            if isinstance(source_obj, (GitHubSource, GitLabSource)):
                infos.append(f"Stance {stance_ref!r} references a remote source (not yet fetched).")
            else:
                errors.append(f"Could not resolve stance {stance_ref!r} because the source does not contain it.")

    for info in infos:
        click.echo(f"  info: {info}")
    for error in errors:
        click.echo(f"  error: {error}")

    if errors:
        raise SystemExit(1)

    click.echo("All checks passed.")
