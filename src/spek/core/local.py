from __future__ import annotations

from pathlib import Path

from spek.core.config import SpekConfig, PROJECT_MODULES_DIR, PROJECT_REFS_DIR, PROJECT_STANCES_DIR

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
    ref = f"project::{name}"
    if ref not in config.modules:
        config.modules.append(ref)
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
    stance_name = stance_path.stem
    ref = f"project::{stance_name}"
    if ref not in config.stances:
        config.stances.append(ref)
        config.save()

    return stance_path


def create_project_ref(name: str) -> Path:
    refs_dir = SpekConfig.root() / PROJECT_REFS_DIR
    ref_path = refs_dir.joinpath(*name.split("/")).with_suffix(".md")
    if ref_path.exists():
        raise FileExistsError(f"{ref_path.relative_to(SpekConfig.root())} already exists.")

    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(REF_STUB)

    return ref_path
