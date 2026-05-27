from __future__ import annotations

from pathlib import Path

from spek.core.config import SpekConfig, PROJECT_MODULES_DIR, PROJECT_REFS_DIR, PROJECT_STANCES_DIR
from spek.core.references import NormalizedTerms, Reference

MODULE_STUB = "# {name}\n\n"
STANCE_STUB = """\
description: "TODO: describe this stance"
modules:
  # List module paths here, e.g.:
  # - ai/behaviors/assume-and-proceed
  # - ai/behaviors/prefer-momentum
"""
REF_STUB = """\
---
spek:
  description: "TODO: describe this reference"
  keywords: []
---

"""


def create_local_module(name: str) -> Path:
    local_dir = SpekConfig.root() / PROJECT_MODULES_DIR
    local_dir.mkdir(parents=True, exist_ok=True)

    module_path = local_dir / f"{name}.md"
    if module_path.exists():
        raise FileExistsError(f"{module_path.relative_to(SpekConfig.root())} already exists.")

    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(MODULE_STUB.format(name=name))

    config = SpekConfig.instance()
    if name not in config.local_modules:
        config.local_modules.append(name)
        config.save()

    return module_path


def create_local_stance(name: str) -> Path:
    root = SpekConfig.root()
    stances_dir = root / PROJECT_STANCES_DIR
    stances_dir.mkdir(parents=True, exist_ok=True)

    filename = name if name.endswith(".yaml") else name + ".yaml"
    stance_path = stances_dir / filename
    if stance_path.exists():
        raise FileExistsError(f"{stance_path.relative_to(root)} already exists.")

    stance_path.write_text(STANCE_STUB)

    config = SpekConfig.instance()
    relative_path = str(stance_path.relative_to(root))
    if relative_path not in config.local_stances:
        config.local_stances.append(relative_path)
        config.save()

    return stance_path


def search_project_refs(terms: list[str] | NormalizedTerms, limit: int = 0, match_all: bool = True) -> list[Reference]:
    if isinstance(terms, list):
        terms = NormalizedTerms(terms)

    refs_dir = SpekConfig.instance().root() / PROJECT_REFS_DIR
    if not refs_dir.exists():
        return []

    scored: list[tuple[int, Reference]] = []
    for src in sorted(refs_dir.rglob("*.md")):
        path = str(src.relative_to(refs_dir).with_suffix(""))
        ref = Reference.load(path, src.read_text())
        score = ref.score(terms)
        if match_all and score < len(terms):
            continue
        if not match_all and score == 0:
            continue
        scored.append((score, ref))

    scored.sort(key=lambda x: x[0], reverse=True)
    scored = scored[:limit] if limit > 0 else scored
    return [r for _, r in scored]


def create_project_ref(name: str) -> Path:
    refs_dir = SpekConfig.instance().root() / PROJECT_REFS_DIR
    ref_path = refs_dir.joinpath(*name.split("/")).with_suffix(".md")
    if ref_path.exists():
        raise FileExistsError(f"{ref_path.relative_to(SpekConfig.instance().root())} already exists.")

    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(REF_STUB)

    return ref_path
