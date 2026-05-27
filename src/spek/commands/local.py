from __future__ import annotations

import click

from spek.commands._utils import load_config_or_exit
from spek.core.local import create_local_module, create_local_stance, create_project_ref


@click.group()
def local() -> None:
    """Manage project-local spec modules and stances."""


@local.command("module")
@click.argument("name")
@click.option("--sync", "run_sync", is_flag=True,
              help="Run spek sync after creating the module.")
def local_module(name: str, run_sync: bool) -> None:
    """Create a new local spec module and register it in spek.yaml."""
    config = load_config_or_exit()
    try:
        module_path = create_local_module(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {module_path.relative_to(config.root())} and registered '{name}' in spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync()
    else:
        click.echo("Run 'spek sync' to generate AI tool output for the new module.")


@local.command("stance")
@click.argument("name")
def local_stance(name: str) -> None:
    """Create a new project-local stance in .spek/local/stances/."""
    config = load_config_or_exit()
    try:
        stance_path = create_local_stance(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {stance_path.relative_to(config.root())} and registered it in spek.yaml.")
    click.echo("Run 'spek sync' so its module dependencies are pulled into .spek/modules/.")


@local.command("ref")
@click.argument("name")
def local_ref(name: str) -> None:
    """Create a new project-local reference entry in .spek/local/references/."""
    config = load_config_or_exit()
    try:
        ref_path = create_project_ref(name)
    except FileExistsError as e:
        click.echo(str(e))
        raise SystemExit(1)

    click.echo(f"Created {ref_path.relative_to(config.root())}.")
