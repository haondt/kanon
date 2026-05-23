from __future__ import annotations

import json as json_mod

import click
import questionary
from questionary import Choice
from pathlib import Path

from spek.core.config import SpekConfig, CONFIG_FILE
from spek.core.modules import list_modules, parse_module_ref, resolve_sources
from spek.core.render import parse_frontmatter
from spek.core.repo import spek_repo_path
from spek.core.settings import load_global_settings


def _resolve_description(name: str, modules_dir: Path, sources: dict[str, Path]) -> str:
    ns, bare = parse_module_ref(name)
    storage_key = f"{ns}/{bare}"
    for base_dir in (modules_dir,):
        p_base = base_dir.joinpath(*storage_key.split("/"))
        for suffix in (".md", ".yaml"):
            p = p_base.with_suffix(suffix)
            if p.exists():
                fm, _ = parse_frontmatter(p.read_text())
                if fm.spek.description:
                    return fm.spek.description
    specs_dir = sources.get(ns)
    if specs_dir:
        p_base = specs_dir.joinpath(*bare.split("/"))
        for suffix in (".md", ".yaml"):
            p = p_base.with_suffix(suffix)
            if p.exists():
                fm, _ = parse_frontmatter(p.read_text())
                if fm.spek.description:
                    return fm.spek.description
    return ""


def _build_sources(root: Path, config: SpekConfig, repo_path: Path) -> dict[str, Path]:
    global_settings = load_global_settings()
    return resolve_sources(
        repo_path,
        {k: v for k, v in global_settings.sources.items()},
        {k: v for k, v in config.sources.items()},
    )


def _all_available(sources: dict[str, Path]) -> list[tuple[str, str]]:
    """Return (qualified_name, namespace) pairs for all available modules across all sources."""
    result: list[tuple[str, str]] = []
    for ns, specs_dir in sources.items():
        if not specs_dir.exists():
            continue
        for bare in list_modules(specs_dir):
            qualified = bare if ns == "spek" else f"{ns}::{bare}"
            result.append((qualified, ns))
    return sorted(result, key=lambda x: x[0])


@click.group()
def module() -> None:
    """Manage modules in spek.yaml."""


@module.command("edit")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_edit(project_root: str, run_sync: bool) -> None:
    """Interactively select modules."""
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
    sources = _build_sources(root, config, repo_path)

    available = _all_available(sources)
    selected_set = set(config.modules)
    choices = [
        Choice(
            title=name,
            checked=(name in selected_set),
            description=_resolve_description(name, modules_dir, sources),
        )
        for name, _ns in available
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
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def module_list(project_root: str, as_json: bool) -> None:
    """List all available modules with descriptions."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE

    selected_set: set[str] = set()
    config: SpekConfig | None = None
    if config_path.exists():
        config = SpekConfig.load(config_path)
        selected_set = set(config.modules)

    repo_path = spek_repo_path()
    modules_dir = root / ".spek" / "modules"
    global_settings = load_global_settings()
    if config is not None:
        sources = resolve_sources(repo_path, dict(global_settings.sources), dict(config.sources))
    else:
        sources = resolve_sources(repo_path, dict(global_settings.sources), {})
    available = _all_available(sources)

    if as_json:
        results = [
            {
                "name": name,
                "description": _resolve_description(name, modules_dir, sources),
                "active": name in selected_set,
                "source": ns,
            }
            for name, ns in available
        ]
        click.echo(json_mod.dumps(results))
        return

    if not available:
        return

    width = max(len(name) for name, _ in available)
    for name, ns in available:
        desc = _resolve_description(name, modules_dir, sources)
        marker = "✓" if name in selected_set else " "
        label = f"[{ns}] " if ns != "spek" else ""
        click.echo(f"  [{marker}] {name:<{width}}  {label}{desc}")


@module.command("set")
@click.argument("modules", nargs=-1, required=True)
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--sync", "run_sync", is_flag=True, help="Run spek sync after saving.")
def module_set(modules: tuple[str, ...], project_root: str, run_sync: bool) -> None:
    """Non-interactively set the module list (full replacement)."""
    root = Path(project_root).resolve()
    config_path = root / CONFIG_FILE
    if not config_path.exists():
        click.echo("No spek.yaml found. Run 'spek init' first.")
        raise SystemExit(1)

    config = SpekConfig.load(config_path)
    repo_path = spek_repo_path()
    sources = _build_sources(root, config, repo_path)
    available_names = {name for name, _ in _all_available(sources)}
    unknown = [m for m in modules if m not in available_names]
    if unknown:
        click.echo(f"Unknown module(s): {', '.join(unknown)}")
        raise SystemExit(1)

    config.modules = list(modules)
    config.save(config_path)
    click.echo(f"Saved {len(modules)} module(s) to spek.yaml.")

    if run_sync:
        from spek.commands.sync import do_sync
        do_sync(root)
    else:
        click.echo("Run 'spek sync' to update AI tool output.")
