from __future__ import annotations

import click

from spek.commands._utils import load_config_or_exit
from spek.core.config import GITHUB_SCHEME, GITLAB_SCHEME, SourceReference, SourcedResource
from spek.core.settings import GlobalSettings
from spek.core.sources import GitHubSource, GitLabSource, LocalSource, hydrate_source_reference, resolve_sources, AliasRef


@click.command("check")
def check() -> None:
    """Check that all configured modules, stances, and sources are valid."""
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

    sources = resolve_sources()

    for module_ref in config.modules:
        module = SourcedResource.parse(module_ref)
        if module.source not in sources:
            if module.source.scheme in (GITHUB_SCHEME, GITLAB_SCHEME):
                infos.append(f"Module {module_ref!r} references a remote source (not yet fetched).")
            else:
                errors.append(f"Could not resolve module {module_ref!r} because the source does not exist.")
        elif not sources[module.source].contains_module(module.path):
            source_obj = sources[module.source]
            if isinstance(source_obj, (GitHubSource, GitLabSource)):
                infos.append(f"Module {module_ref!r} references a remote source (not yet fetched).")
            else:
                errors.append(f"Could not resolve module {module_ref!r} because the source does not contain it.")

    for stance_ref in config.stances:
        stance = SourcedResource.parse(stance_ref)
        if stance.source not in sources:
            if stance.source.scheme in (GITHUB_SCHEME, GITLAB_SCHEME):
                infos.append(f"Stance {stance_ref!r} references a remote source (not yet fetched).")
            else:
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
