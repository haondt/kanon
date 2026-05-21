from __future__ import annotations

import shutil
import click
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE
from spek.core.render import AI_TOOL_OUTPUT_DIRS


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

    targets: list[Path] = [root / ".spek"]
    seen: set[Path] = set()
    for integration in config.meta.integrations:
        tool_dirs = AI_TOOL_OUTPUT_DIRS.get(integration, {})
        for rel in tool_dirs.values():
            p = root / rel
            if p not in seen:
                seen.add(p)
                targets.append(p)

    existing = [t for t in targets if t.exists()]

    click.echo("Will remove:")
    for t in existing:
        click.echo(f"  {t.relative_to(root)}")

    if not yes:
        click.confirm("Proceed?", default=False, abort=True)

    for t in existing:
        shutil.rmtree(t)
        click.echo(f"  removed {t.relative_to(root)}")

    click.echo("Done.")
