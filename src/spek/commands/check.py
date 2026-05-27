from __future__ import annotations

import click

from spek.commands._utils import load_config_or_exit
from spek.core.config import SourcedResource
from spek.core.settings import GlobalSettings
from spek.core.sources import GitHubSource, GitLabSource, LocalSource, parse_source_ref, resolve_sources


@click.command("check")
def check() -> None:
    """Check that all configured modules and sources are valid."""
    config = load_config_or_exit()
    global_settings = GlobalSettings.instance()

    errors: list[str] = []
    infos: list[str] = []

    for source in (global_settings.sources, config.sources):
        for label, path in source.items():
            try:
                parsed = parse_source_ref(path)
            except ValueError as e:
                errors.append(f"Invalid source path for {label}: {e}")
                continue
            if isinstance(parsed, LocalSource):
                if not parsed.root.exists():
                    errors.append(f"Source {label!r} path does not exist: {parsed.root}")
            elif isinstance(parsed, (GitHubSource, GitLabSource)):
                infos.append(f"Source {label!r} is remote — not yet supported: {path}")

    sources = resolve_sources()

    for module_ref in config.modules:
        module = SourcedResource.parse(module_ref)
        if module.source not in sources:
            errors.append(f"Could not resolve module {module_ref!r} because the source does not exist.")
        elif not sources[module.source].contains_module(module.path):
            errors.append(f"Could not resolve module {module_ref!r} because the source does not contain it.")

    for info in infos:
        click.echo(f"  info: {info}")
    for error in errors:
        click.echo(f"  error: {error}")

    if errors:
        raise SystemExit(1)

    click.echo("All checks passed.")
