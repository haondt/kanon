from __future__ import annotations

import click
import questionary
from questionary import Choice
from pathlib import Path

from spek import __version__
from spek.core.config import SpekConfig, SpekMeta, CONFIG_FILE
from spek.core.modules import list_modules
from spek.core.repo import spek_repo_path, spek_sha
from spek.core.profiles import resolve_profile, list_profiles
from spek.core.render import AI_TOOL_OUTPUT_DIRS

INTEGRATIONS = list(AI_TOOL_OUTPUT_DIRS)


@click.command()
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
def init(project_root: str) -> None:
    """Interactively initialize a new project with spek conventions."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE

    if config_path.exists():
        click.echo(".spek/spek.yaml already exists. Run 'spek sync' to update.")
        raise SystemExit(1)

    config_path.parent.mkdir(parents=True, exist_ok=True)

    gitignore_path = config_path.parent / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("SESSION.md\n")

    repo_path = spek_repo_path()
    profiles_dir = repo_path / "profiles"
    profiles = list_profiles(profiles_dir)
    modules = list_modules(repo_path)

    integrations = questionary.checkbox(
        "Select integrations:",
        choices=INTEGRATIONS,
        use_jk_keys=False,
    ).ask()
    if not integrations:
        click.echo("No integrations selected. Aborting.")
        raise SystemExit(1)

    selected_modules: list[str] = []
    selected_stances: list[str] = []
    chosen_profile: str | None = None

    if profiles:
        profile_choice = questionary.select(
            "Start from a profile?",
            choices=["none"] + list(profiles.keys()),
            use_jk_keys=False,
        ).ask()
        if profile_choice is None:
            raise SystemExit(1)
        if profile_choice != "none":
            chosen_profile = profile_choice
            selected_modules, selected_stances = resolve_profile(profile_choice, profiles_dir)
            click.echo(f"Loaded {len(selected_modules)} modules and {len(selected_stances)} stances from '{profile_choice}'.")

    module_choices = [Choice(m, checked=(m in selected_modules)) for m in modules]
    selected_modules = questionary.checkbox(
        "Select modules:",
        choices=module_choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()
    if not selected_modules:
        click.echo("No modules selected. Aborting.")
        raise SystemExit(1)

    sha = spek_sha(repo_path)
    config = SpekConfig(
        meta=SpekMeta(spek_version=__version__, spek_sha=sha, integrations=integrations, profile=chosen_profile),
        modules=selected_modules,
        stances=selected_stances,
    )
    config.save(config_path)
    click.echo(f"\nWrote .spek/spek.yaml with {len(selected_modules)} module(s) pinned at {sha[:8]}.")
    click.echo("Run 'spek sync' to copy spec files and emit AI tool rules.")
