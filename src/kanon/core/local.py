from __future__ import annotations

from pathlib import Path

from kanon.core.config import KanonConfig, PROJECT_KANONS_DIR, PROJECT_REFS_DIR, PROJECT_STANCES_DIR

KANON_STUB = "# {name}\n\n"
STANCE_STUB = """\
description: "TODO: describe this stance"
kanons:
  # List kanon paths here, e.g.:
  # - ai/behaviors/assume-and-proceed
  # - ai/behaviors/prefer-momentum
"""
REF_STUB = """\
---
kanon:
  description: "TODO: describe this reference"
  keywords: []
---

"""


def create_local_kanon(name: str) -> Path:
    local_dir = KanonConfig.root() / PROJECT_KANONS_DIR
    local_dir.mkdir(parents=True, exist_ok=True)

    kanon_path = local_dir / f"{name}.md"
    if kanon_path.exists():
        raise FileExistsError(f"{kanon_path.relative_to(KanonConfig.root())} already exists.")

    kanon_path.parent.mkdir(parents=True, exist_ok=True)
    kanon_path.write_text(KANON_STUB.format(name=name))

    config = KanonConfig.instance()
    ref = f"project::{name}"
    if ref not in config.kanons:
        config.kanons.append(ref)
        config.save()

    return kanon_path


def create_local_stance(name: str) -> Path:
    root = KanonConfig.root()
    stances_dir = root / PROJECT_STANCES_DIR
    stances_dir.mkdir(parents=True, exist_ok=True)

    filename = name if name.endswith(".yaml") else name + ".yaml"
    stance_path = stances_dir / filename
    if stance_path.exists():
        raise FileExistsError(f"{stance_path.relative_to(root)} already exists.")

    stance_path.write_text(STANCE_STUB)

    config = KanonConfig.instance()
    stance_name = stance_path.stem
    ref = f"project::{stance_name}"
    if ref not in config.stances:
        config.stances.append(ref)
        config.save()

    return stance_path


def create_project_ref(name: str) -> Path:
    refs_dir = KanonConfig.root() / PROJECT_REFS_DIR
    ref_path = refs_dir.joinpath(*name.split("/")).with_suffix(".md")
    if ref_path.exists():
        raise FileExistsError(f"{ref_path.relative_to(KanonConfig.root())} already exists.")

    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(REF_STUB)

    return ref_path
