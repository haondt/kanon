from __future__ import annotations

from pathlib import Path


def list_modules(repo_path: Path) -> list[str]:
    specs_dir = repo_path / "specs"
    seen: set[str] = set()
    modules: list[str] = []
    for src in sorted(specs_dir.rglob("*.md")) + sorted(specs_dir.rglob("*.yaml")):
        rel = str(src.relative_to(specs_dir).with_suffix(""))
        if rel not in seen:
            seen.add(rel)
            modules.append(rel)
    return sorted(modules)
