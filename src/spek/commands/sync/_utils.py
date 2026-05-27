from __future__ import annotations

from pathlib import Path

from spek.core.yaml_utils import load_yaml


def find(name: str, search_dir: Path, suffixes: tuple[str, ...] = (".md", ".yaml")) -> Path | None:
    base = search_dir.joinpath(*name.split("/"))
    for suffix in suffixes:
        p = base.with_suffix(suffix)
        if p.exists():
            return p
    return None


def load_stance_modules(stance_path: Path) -> list[str]:
    return load_yaml(stance_path).get("modules", [])
