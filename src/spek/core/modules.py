from __future__ import annotations

from pathlib import Path

from spek.core.config import SPEK_NAMESPACE


def list_modules(specs_dir: Path) -> list[str]:
    seen: set[str] = set()
    modules: list[str] = []
    for src in sorted(specs_dir.rglob("*.md")) + sorted(specs_dir.rglob("*.yaml")):
        rel = str(src.relative_to(specs_dir).with_suffix(""))
        if rel not in seen:
            seen.add(rel)
            modules.append(rel)
    return sorted(modules)


def parse_module_ref(name: str) -> tuple[str, str]:
    """Split 'ns::bare/path' into ('ns', 'bare/path'). Defaults to ('spek', name)."""
    if "::" in name:
        ns, bare = name.split("::", 1)
        return ns, bare
    return "spek", name


def resolve_sources(
    repo_path: Path | None,
    global_sources: dict,
    project_sources: dict,
) -> dict[str, Path]:
    """Merge global + project sources (project wins).

    'spek' namespace may be overridden by either sources dict; if not provided,
    it defaults to repo_path / 'specs' when repo_path is not None.
    """
    merged: dict[str, Path] = {}
    for ns, spec in global_sources.items():
        merged[ns] = Path(spec.path)
    for ns, spec in project_sources.items():
        merged[ns] = Path(spec.path)
    if SPEK_NAMESPACE not in merged and repo_path is not None:
        merged[SPEK_NAMESPACE] = repo_path / "specs"
    return merged
