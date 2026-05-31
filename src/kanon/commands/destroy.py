from __future__ import annotations

import shutil
import click
from pathlib import Path

from kanon.core.config import AI_TOOL_OUTPUT_DIRS, AI_TOOL_SETTINGS_FILES, KanonConfig


@click.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def destroy(yes: bool) -> None:
    """Remove all kanon-managed files from a project."""
    config = KanonConfig.get()
    if not config:
        click.echo("No kanon.yaml found. Nothing to destroy.")
        raise SystemExit(0)

    dir_targets: list[Path] = [KanonConfig.root()]
    file_targets: list[Path] = []
    seen: set[Path] = set()
    for integration in config.meta.integrations:
        tool_dirs = AI_TOOL_OUTPUT_DIRS.get(integration, {})
        for rel in tool_dirs.values():
            p = config.project_root() / rel
            if p not in seen:
                seen.add(p)
                dir_targets.append(p)
        settings_rel = AI_TOOL_SETTINGS_FILES.get(integration)
        if settings_rel:
            p = config.project_root() / settings_rel
            if p not in seen:
                seen.add(p)
                file_targets.append(p)

    existing_dirs = [t for t in dir_targets if t.exists()]
    existing_files = [t for t in file_targets if t.exists()]

    click.echo("Will remove:")
    for t in existing_dirs + existing_files:
        click.echo(f"  {t.relative_to(config.project_root())}")

    if not yes:
        click.confirm("Proceed?", default=False, abort=True)

    for t in existing_dirs:
        shutil.rmtree(t)
        click.echo(f"  removed {t.relative_to(config.project_root())}")
    for t in existing_files:
        t.unlink()
        click.echo(f"  removed {t.relative_to(config.project_root())}")

    click.echo("Done.")
