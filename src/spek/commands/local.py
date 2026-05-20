from __future__ import annotations

import click
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE, LOCAL_MODULES_DIR, LOCAL_STANCES_DIR

MODULE_STUB = "# {name}\n\n"
STANCE_STUB = """\
description: "TODO: describe this stance"
modules:
  # List module paths here, e.g.:
  # - ai/behaviors/assume-and-proceed
  # - ai/behaviors/prefer-momentum
"""


@click.group()
def local() -> None:
    """Manage project-local spec modules and stances."""


@local.command("module")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
@click.option("--sync", "run_sync", is_flag=True,
              help="Run spek sync after creating the module.")
def local_module(name: str, project_root: str, run_sync: bool) -> None:
    """Create a new local spec module and register it in spek.yaml."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE

    if not config_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    local_dir = root / LOCAL_MODULES_DIR
    local_dir.mkdir(parents=True, exist_ok=True)

    filename = name if name.endswith(".md") else name + ".md"
    module_path = local_dir / filename
    relative_path = str(module_path.relative_to(root))

    if module_path.exists():
        click.echo(f"{relative_path} already exists.")
        raise SystemExit(1)

    module_path.write_text(MODULE_STUB.format(name=name))

    config = SpekConfig.load(config_path)
    if relative_path not in config.local_modules:
        config.local_modules.append(relative_path)
        config.save(config_path)

    click.echo(f"Created {relative_path} and registered it in spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync(root)
    else:
        click.echo("Run 'spek sync' to generate AI tool output for the new module.")


@local.command("stance")
@click.argument("name")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
def local_stance(name: str, project_root: str) -> None:
    """Create a new project-local stance in .spek/local/stances/."""
    root = Path(project_root).resolve()
    stances_dir = root / LOCAL_STANCES_DIR
    stances_dir.mkdir(parents=True, exist_ok=True)

    filename = name if name.endswith(".yaml") else name + ".yaml"
    stance_path = stances_dir / filename
    relative_path = str(stance_path.relative_to(root))

    if stance_path.exists():
        click.echo(f"{relative_path} already exists.")
        raise SystemExit(1)

    config_path = root / CONFIG_FILE
    if not config_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    stance_path.write_text(STANCE_STUB.format(name=name))

    config = SpekConfig.load(config_path)
    if relative_path not in config.local_stances:
        config.local_stances.append(relative_path)
        config.save(config_path)

    click.echo(f"Created {relative_path} and registered it in spek.yaml.")
    click.echo("Run 'spek sync' so its module dependencies are pulled into .spek/modules/.")
