from __future__ import annotations

import shutil
import click
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE
from spek.core.render import AI_TOOL_OUTPUT_DIRS, AI_TOOL_SETTINGS_FILES


@click.command()
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def destroy(project_root: str, yes: bool) -> None:
    """Remove all spek-managed files from a project."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE

    if not config_path.exists():
        click.echo("No spek.yaml found. Nothing to destroy.")
        raise SystemExit(0)

    config = SpekConfig.load(config_path)

    dir_targets: list[Path] = [root / ".spek"]
    file_targets: list[Path] = []
    seen: set[Path] = set()
    for integration in config.meta.integrations:
        tool_dirs = AI_TOOL_OUTPUT_DIRS.get(integration, {})
        for rel in tool_dirs.values():
            p = root / rel
            if p not in seen:
                seen.add(p)
                dir_targets.append(p)
        settings_rel = AI_TOOL_SETTINGS_FILES.get(integration)
        if settings_rel:
            p = root / settings_rel
            if p not in seen:
                seen.add(p)
                file_targets.append(p)

    existing_dirs = [t for t in dir_targets if t.exists()]
    existing_files = [t for t in file_targets if t.exists()]

    click.echo("Will remove:")
    for t in existing_dirs + existing_files:
        click.echo(f"  {t.relative_to(root)}")

    if not yes:
        click.confirm("Proceed?", default=False, abort=True)

    for t in existing_dirs:
        shutil.rmtree(t)
        click.echo(f"  removed {t.relative_to(root)}")
    for t in existing_files:
        t.unlink()
        click.echo(f"  removed {t.relative_to(root)}")

    click.echo("Done.")
