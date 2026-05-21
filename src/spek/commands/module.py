from __future__ import annotations

import click
import questionary
from questionary import Choice
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE
from spek.core.modules import list_modules
from spek.core.render import parse_frontmatter
from spek.core.repo import spek_repo_path


def _resolve_description(name: str, modules_dir: Path, specs_dir: Path) -> str:
    for base_dir in (modules_dir, specs_dir):
        p_base = base_dir.joinpath(*name.split("/"))
        for suffix in (".md", ".yaml"):
            p = p_base.with_suffix(suffix)
            if p.exists():
                fm, _ = parse_frontmatter(p.read_text())
                if fm.spek.description:
                    return fm.spek.description
    return ""


@click.group(invoke_without_command=True)
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
@click.pass_context
def module(ctx: click.Context, project_root: str, run_sync: bool) -> None:
    """Manage modules in spek.yaml."""
    if ctx.invoked_subcommand is None:
        _do_picker(project_root, run_sync)


def _do_picker(project_root: str, run_sync: bool) -> None:
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE
    if not config_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    config = SpekConfig.load(config_path)
    repo_path = spek_repo_path()
    modules_dir = root / ".spek" / "modules"
    specs_dir = repo_path / "specs"
    available = list_modules(repo_path)

    selected_set = set(config.modules)
    choices = [
        Choice(
            title=name,
            checked=(name in selected_set),
            description=_resolve_description(name, modules_dir, specs_dir),
        )
        for name in available
    ]

    result = questionary.checkbox(
        "Select modules:",
        choices=choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if not result:
        click.echo("No modules selected. Aborting.")
        raise SystemExit(1)

    config.modules = result
    config.save(config_path)
    click.echo(f"Saved {len(result)} module(s) to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync(root)
    else:
        click.echo("Run 'spek sync' to update AI tool output.")


@module.command("list")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
def module_list(project_root: str) -> None:
    """List all available modules with descriptions."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE

    selected_set: set[str] = set()
    if config_path.exists():
        config = SpekConfig.load(config_path)
        selected_set = set(config.modules)

    repo_path = spek_repo_path()
    modules_dir = root / ".spek" / "modules"
    specs_dir = repo_path / "specs"
    available = list_modules(repo_path)

    width = max(len(m) for m in available)
    for name in available:
        desc = _resolve_description(name, modules_dir, specs_dir)
        marker = "✓" if name in selected_set else " "
        click.echo(f"  [{marker}] {name:<{width}}  {desc}")
