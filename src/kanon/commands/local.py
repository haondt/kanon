from __future__ import annotations

import click

from kanon.commands._utils import load_config_or_exit
from kanon.core.local import create_local_kanon, create_local_stance, create_project_ref


@click.group()
def local() -> None:
    """Manage project-local kanons, stances, and references."""


@local.command("kanon")
@click.argument("name")
@click.option("--sync", "run_sync", is_flag=True,
              help="Run kanon sync after creating the kanon.")
def local_kanon(name: str, run_sync: bool) -> None:
    """Create a new local kanon and register it in kanon.yaml."""
    config = load_config_or_exit()
    try:
        kanon_path = create_local_kanon(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {kanon_path.relative_to(config.root())} and registered '{name}' in kanon.yaml.")

    if run_sync:
        from kanon.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'kanon sync' to generate AI tool output for the new kanon.")


@local.command("stance")
@click.argument("name")
def local_stance(name: str) -> None:
    """Create a new project-local stance in .kanon/local/stances/."""
    config = load_config_or_exit()
    try:
        stance_path = create_local_stance(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {stance_path.relative_to(config.root())} and registered it in kanon.yaml.")
    click.echo("Run 'kanon sync' so its kanon dependencies are pulled into .kanon/kanons/.")


@local.command("ref")
@click.argument("name")
def local_ref(name: str) -> None:
    """Create a new project-local reference entry in .kanon/local/references/."""
    config = load_config_or_exit()
    try:
        ref_path = create_project_ref(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {ref_path.relative_to(config.root())}.")
