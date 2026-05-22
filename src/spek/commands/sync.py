from __future__ import annotations

import shutil
import click
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE, MODULES_DIR, STANCES_DIR, LOCAL_MODULES_DIR
from spek.core.yaml_utils import load_yaml


def _find(name: str, search_dir: Path, suffixes: tuple[str, ...] = (".md", ".yaml")) -> Path | None:
    base = search_dir.joinpath(*name.split("/"))
    for suffix in suffixes:
        p = base.with_suffix(suffix)
        if p.exists():
            return p
    return None


def _copy_to(src: Path, dest_dir: Path, rel_name: str) -> Path:
    dst = dest_dir.joinpath(*rel_name.split("/")).with_suffix(src.suffix)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    return dst


def _prune(directory: Path, expected: set[Path]) -> None:
    for f in list(directory.rglob("*")):
        if f.is_file() and f not in expected:
            f.unlink()
    for d in sorted(directory.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def _load_stance_modules(stance_path: Path) -> list[str]:
    return load_yaml(stance_path).get("modules", [])


def do_sync(root: Path, pull: bool = False) -> None:
    """Core sync logic — callable programmatically from other commands."""
    config_path = root / CONFIG_FILE
    if not config_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    config = SpekConfig.load(config_path)
    modules_dir = root / MODULES_DIR
    stances_dir = root / STANCES_DIR
    modules_dir.mkdir(parents=True, exist_ok=True)
    stances_dir.mkdir(parents=True, exist_ok=True)

    # Resolve upstream repo (optional — only needed when pulling missing files)
    try:
        from spek.core.repo import spek_repo_path, spek_sha
        repo_path = spek_repo_path()
        upstream_specs: Path | None = repo_path / "specs"
        upstream_stances: Path | None = repo_path / "stances"
    except Exception:
        repo_path = None
        upstream_specs = None
        upstream_stances = None

    # ── Phase 0: --pull — force-refresh all stances and modules ────────────────
    if pull:
        if upstream_specs is None:
            click.echo("Cannot locate spek repo — --pull requires it.")
            raise SystemExit(1)
        click.echo("Pulling from upstream:")
        for stance_name in config.stances:
            src = _find(stance_name, upstream_stances, (".yaml",))
            if src:
                _copy_to(src, stances_dir, stance_name)
                click.echo(f"  stance:{stance_name} ← upstream")
            else:
                click.echo(f"  WARNING: stance '{stance_name}' not found upstream.")

    # ── Phase 1: reconcile stances in .spek/stances/ ─────────────────────────
    expected_stances: set[Path] = set()
    for stance_name in config.stances:
        local = _find(stance_name, stances_dir, (".yaml",))
        if local:
            expected_stances.add(local)
        elif upstream_stances:
            src = _find(stance_name, upstream_stances, (".yaml",))
            if src:
                dst = _copy_to(src, stances_dir, stance_name)
                expected_stances.add(dst)
                click.echo(f"  pulled stance '{stance_name}' from upstream")
            else:
                click.echo(f"  WARNING: stance '{stance_name}' not found locally or upstream.")
        else:
            click.echo(f"  WARNING: stance '{stance_name}' missing and no upstream available.")

    _prune(stances_dir, expected_stances)

    # ── Phase 2: collect all modules needed (direct + from all stances) ───────
    direct_modules: set[str] = set(config.modules)
    stance_modules: set[str] = set()

    for stance_path in expected_stances:
        for mod in _load_stance_modules(stance_path):
            stance_modules.add(mod)

    for local_stance_path in config.local_stances:
        abs_path = (root / local_stance_path).resolve()
        if abs_path.exists():
            for mod in _load_stance_modules(abs_path):
                stance_modules.add(mod)
        else:
            click.echo(f"  WARNING: local stance '{local_stance_path}' not found, skipping.")

    all_modules_needed = direct_modules | stance_modules

    # ── Phase 3 (--pull): force-refresh all modules ─────────────────────────────
    if pull and upstream_specs:
        for mod in all_modules_needed:
            src = _find(mod, upstream_specs)
            if src:
                _copy_to(src, modules_dir, mod)
                click.echo(f"  {mod} ← upstream")
            else:
                click.echo(f"  WARNING: module '{mod}' not found upstream.")

    # ── Phase 4: reconcile modules in .spek/modules/ ─────────────────────────
    expected_modules: set[Path] = set()
    for mod in all_modules_needed:
        local = _find(mod, modules_dir)
        if local:
            expected_modules.add(local)
        elif upstream_specs:
            src = _find(mod, upstream_specs)
            if src:
                dst = _copy_to(src, modules_dir, mod)
                expected_modules.add(dst)
                click.echo(f"  pulled '{mod}' from upstream")
            else:
                click.echo(f"  WARNING: module '{mod}' not found locally or upstream, skipping.")
        else:
            click.echo(f"  WARNING: module '{mod}' missing and no upstream available.")

    _prune(modules_dir, expected_modules)

    if pull:
        if repo_path is not None:
            new_sha = spek_sha(repo_path)
            click.echo(f"Recording SHA {new_sha[:8]}.")
            config.meta.spek_sha = new_sha
            config.save(config_path)

    # ── Phase 5: generate AI tool output ──────────────────────────────────────
    # Only modules in config.modules (not stance-only) become rules/commands.
    from spek.core.render import AI_TOOL_OUTPUT_DIRS, render_module

    to_render: list[tuple[str, Path]] = []
    for mod in config.modules:
        p = _find(mod, modules_dir)
        if p:
            to_render.append((mod, p))

    local_modules_dir = root / LOCAL_MODULES_DIR
    for name in config.local_modules:
        p = _find(name, local_modules_dir)
        if p:
            to_render.append((name, p))
        else:
            click.echo(f"  WARNING: local module '{name}' not found, skipping.")

    for integration in config.meta.integrations:
        for rel_dir in set(AI_TOOL_OUTPUT_DIRS.get(integration, {}).values()):
            d = root / rel_dir
            if d.exists():
                shutil.rmtree(d)

    for integration in config.meta.integrations:
        click.echo(f"Generating {integration} output:")
        for name, src in to_render:
            content = src.read_text()
            out_path = render_module(content, name, integration, root)
            click.echo(f"  {name} → {out_path.relative_to(root)}")

    click.echo("Done.")


@click.command()
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False),
              help="Root of the target project (default: current directory).")
@click.option("--pull", is_flag=True,
              help="Force-refresh all stances and modules from the upstream spek repo and record SHA.")
def sync(project_root: str, pull: bool) -> None:
    """Sync spec modules and stances, then generate AI tool output.

    Reads from .spek/modules/ and .spek/stances/ (local committed copies).
    Missing files are pulled from the upstream spek repo automatically.
    Use --pull to force-refresh everything from the spek repo and record SHA.
    Only modules listed in spek.yaml.modules become rules/commands.
    Modules referenced only by stances stay in .spek/modules/ and are inert
    until activated via /spek-stance.
    """
    do_sync(Path(project_root).resolve(), pull=pull)
