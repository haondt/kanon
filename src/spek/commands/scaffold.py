from __future__ import annotations

import click
from pathlib import Path

from spek import __version__
from spek.core.config import SpekConfig, SpekMeta, CONFIG_FILE
from spek.core.repo import spek_repo_path, spek_sha
from spek.core.profiles import resolve_profile, list_profiles

AI_TOOLS = ["claude", "windsurf"]


def _available_modules(repo_path: Path) -> list[str]:
    specs_dir = repo_path / "specs"
    seen: set[str] = set()
    modules = []
    for src in sorted(specs_dir.rglob("*.md")) + sorted(specs_dir.rglob("*.yaml")):
        rel = str(src.relative_to(specs_dir).with_suffix(""))
        if rel not in seen:
            seen.add(rel)
            modules.append(rel)
    return sorted(modules)




@click.command()
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
def scaffold(project_root: str) -> None:
    """Interactively scaffold a new project with spek conventions."""
    root = Path(project_root).resolve()
    lock_path = root / CONFIG_FILE

    if lock_path.exists():
        click.echo(".spek/spek.yaml already exists. Run 'spek sync' to update.")
        raise SystemExit(1)

    lock_path.parent.mkdir(parents=True, exist_ok=True)

    repo_path = spek_repo_path()
    profiles_dir = repo_path / "profiles"
    profiles = list_profiles(profiles_dir)
    modules = _available_modules(repo_path)

    # Choose AI tool
    ai_tool = click.prompt(
        "AI tool",
        type=click.Choice(AI_TOOLS),
        default="claude",
    )

    selected_modules: list[str] = []
    chosen_profile: str | None = None

    # Optionally start from a profile
    selected_stances: list[str] = []

    if profiles:
        profile_names = list(profiles.keys())
        click.echo(f"\nAvailable profiles: {', '.join(profile_names)} (or 'none')")
        profile_choice = click.prompt("Start from a profile?", default="none")
        if profile_choice in profiles:
            chosen_profile = profile_choice
            selected_modules, selected_stances = resolve_profile(profile_choice, profiles_dir)
            click.echo(f"Loaded {len(selected_modules)} modules and {len(selected_stances)} stances from profile '{profile_choice}'.")

    # Pick individual modules
    click.echo("\nAvailable modules:")
    for i, m in enumerate(modules, 1):
        marker = "✓" if m in selected_modules else " "
        click.echo(f"  [{marker}] {i:2}. {m}")

    click.echo("\nEnter module numbers to toggle (comma-separated), or press Enter to continue.")
    raw = click.prompt("Modules to add", default="", show_default=False)
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            idx = int(token) - 1
            mod = modules[idx]
            if mod not in selected_modules:
                selected_modules.append(mod)
        except (ValueError, IndexError):
            click.echo(f"  Ignored: {token!r}")

    if not selected_modules:
        click.echo("No modules selected. Aborting.")
        raise SystemExit(1)

    sha = spek_sha(repo_path)
    lock = SpekConfig(
        meta=SpekMeta(spek_version=__version__, spek_sha=sha, ai_tool=ai_tool, profile=chosen_profile),
        modules=selected_modules,
        stances=selected_stances,
    )
    lock.save(lock_path)
    click.echo(f"\nWrote .spek/spek.yaml with {len(selected_modules)} module(s) pinned at {sha[:8]}.")
    click.echo("Run 'spek sync' to copy spec files and emit AI tool rules.")
