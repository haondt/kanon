from __future__ import annotations

import shutil
from typing import Any

import click

from spek.core.config import SourceReference, SpekEnv
from spek.core.sources import SourceResolver


@click.group()
def cache() -> None:
    """Manage the local source cache."""


@cache.command("status")
def cache_status() -> None:
    """Show disk usage of the source cache."""
    cache_dir = SpekEnv.instance().sources_cache_path
    if not cache_dir.exists():
        click.echo("Cache is empty.")
        return

    rows: list[Any] = []
    for scheme_dir in sorted(cache_dir.iterdir()):
        if not scheme_dir.is_dir():
            continue
        for entry in sorted(scheme_dir.rglob("*")):
            if not entry.is_dir():
                continue
            # only include leaf directories (no subdirectories that are also cache roots)
            # walk up looking for repos: a git repo is a leaf cache entry
            if (entry / ".git").exists():
                size = sum(f.stat().st_size for f in entry.rglob("*") if f.is_file())
                rel = entry.relative_to(cache_dir)
                scheme = rel.parts[0]
                path = str(rel.relative_to(scheme))
                rows.append({"scheme": scheme, "path": path, "size": size})

    if not rows:
        click.echo("Cache is empty.")
        return

    scheme_w = max(len(r["scheme"]) for r in rows)
    path_w = max(len(r["path"]) for r in rows)
    click.echo(f"  {'scheme':<{scheme_w}}  {'path':<{path_w}}  size")
    click.echo(f"  {'-' * scheme_w}  {'-' * path_w}  ----")
    for r in rows:
        size_kb = r["size"] / 1024
        if size_kb >= 1024:
            size_str = f"{size_kb / 1024:.1f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"
        click.echo(f"  {r['scheme']:<{scheme_w}}  {r['path']:<{path_w}}  {size_str}")


@cache.command("clear")
@click.argument("name", required=False, default=None)
def cache_clear(name: str | None) -> None:
    """Clear the source cache.

    With no arguments, clears the entire cache directory.
    With NAME, clears only the named source's cache (alias or direct reference).
    """
    if name is None:
        cache_dir = SpekEnv.instance().sources_cache_path
        shutil.rmtree(cache_dir, ignore_errors=True)
        click.echo("Cache cleared.")
        return

    resolved = SourceResolver.instance()
    ref = SourceReference.parse(name, sanitize=True)
    try:
        src = resolved[ref]
    except ValueError:
        click.echo(f"Unknown source: {name!r}")
        raise SystemExit(1)
    path = src.cache_path()
    if path is None:
        click.echo(f"{ref.as_string} has no cache (not a remote source).")
        return

    if path.exists():
        shutil.rmtree(path)
        click.echo(f"Cleared cache for {ref.as_string}.")
    else:
        click.echo(f"No cache found for {ref.as_string}.")
