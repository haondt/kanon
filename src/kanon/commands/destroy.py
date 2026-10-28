from __future__ import annotations

from pathlib import Path
import shutil

import click

from kanon.core.config import KanonConfig
from kanon.core.render import DryCleanResult, clean_all, dry_clean_all, roots
from kanon.commands._utils import exit_ok


@click.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def destroy(yes: bool) -> None:
    """Remove all kanon-managed files from a project."""
    config = KanonConfig.get()
    if not config:
        exit_ok("No kanon.yaml found. Nothing to destroy.")


    dry_cleans: list[DryCleanResult] = []
    integration_roots: list[Path] = []
    for integration in config.meta.integrations:
        dry_cleans.append(dry_clean_all(integration))
        integration_roots.append(roots(integration).output_root)


    if config.is_global():
        last_root = config.project_root()
        click.echo(f"Will remove from {last_root}:")
        click.echo(f"  {KanonConfig.root().relative_to(config.project_root())}")
        for dry_clean, global_root in zip(dry_cleans, integration_roots):
            if global_root != last_root:
                last_root = global_root
                click.echo(f"Will remove from {last_root}:")
            for t in dry_clean.directories + dry_clean.files:
                click.echo(f"  {t.relative_to(last_root)}")
            if dry_clean.extra_info:
                click.echo(f"{dry_clean.extra_info}")
    else:
        dry_clean = DryCleanResult.merge(dry_cleans)

        click.echo("Will remove:")
        click.echo(f"  {KanonConfig.root().relative_to(config.project_root())}")
        for t in dry_clean.directories + dry_clean.files:
            click.echo(f"  {t.relative_to(config.project_root())}")
            if dry_clean.extra_info:
                click.echo(dry_clean.extra_info)

    if not yes:
        click.confirm("Proceed?", default=False, abort=True)

    for integration in config.meta.integrations:
        clean_all(integration, click.echo)
    shutil.rmtree(KanonConfig.root())
    click.echo(f"  removed {KanonConfig.root().relative_to(config.project_root())}")

    click.echo("Done.")
