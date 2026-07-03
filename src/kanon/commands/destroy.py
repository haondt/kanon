from __future__ import annotations

import shutil

import click

from kanon.core.config import KanonConfig
from kanon.core.render import DryCleanResult, clean_all, dry_clean_all


@click.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def destroy(yes: bool) -> None:
    """Remove all kanon-managed files from a project."""
    config = KanonConfig.get()
    if not config:
        click.echo("No kanon.yaml found. Nothing to destroy.")
        raise SystemExit(0)

    dry_cleans: list[DryCleanResult] = []
    for integration in config.meta.integrations:
        dry_cleans.append(dry_clean_all(integration))
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
