from __future__ import annotations

import click
from pathlib import Path

from spek.core.profiles import resolve_profile, list_profiles
from spek.core.repo import spek_repo_path
from spek.core.config import SpekConfig, CONFIG_FILE


@click.group()
def profile() -> None:
    """Inspect and apply profiles."""


@profile.command("list")
def profile_list() -> None:
    """List all available profiles."""
    repo_path = spek_repo_path()
    profiles = list_profiles(repo_path / "profiles")
    if not profiles:
        click.echo("No profiles found.")
        return
    width = max(len(k) for k in profiles)
    for name, description in profiles.items():
        click.echo(f"  {name:<{width}}  {description}")


@profile.command("apply")
@click.argument("name", required=False)
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
@click.option("--sync", "run_sync", is_flag=True,
              help="Run spek sync after applying the profile.")
def profile_apply(name: str | None, project_root: str, run_sync: bool) -> None:
    """Re-resolve a profile and update modules in spek.yaml.

    Uses the profile recorded in spek.yaml if NAME is omitted.
    local_modules are preserved unchanged.
    """
    root = Path(project_root).resolve()
    lock_path = root / CONFIG_FILE

    if not lock_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    lock = SpekConfig.load(lock_path)
    profile_name = name or lock.meta.profile

    if not profile_name:
        click.echo("No profile recorded in spek.yaml and no NAME given.")
        raise SystemExit(1)

    repo_path = spek_repo_path()
    profiles_dir = repo_path / "profiles"

    try:
        modules, stances = resolve_profile(profile_name, profiles_dir)
    except FileNotFoundError as e:
        click.echo(str(e))
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e))
        raise SystemExit(1)
    lock.modules = modules
    lock.stances = stances
    lock.meta.profile = profile_name
    lock.save(lock_path)
    click.echo(f"Applied profile '{profile_name}': {len(modules)} module(s), {len(stances)} stance(s) written to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync(root)
    else:
        click.echo("Run 'spek sync' to update AI tool output.")
