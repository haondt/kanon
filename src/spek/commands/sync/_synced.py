from __future__ import annotations

from pathlib import Path

from spek.core.config import SYNCED_MODULES_DIR, SYNCED_STANCES_DIR, SourceReference, SourcedResource, SpekConfig
from spek.core.modules import Module
from spek.core.sources import SourceResolver
from spek.core.stances import Stance

def _modules_path() -> Path:
    return SpekConfig.root() / SYNCED_MODULES_DIR

def _stances_path() -> Path:
    return SpekConfig.root() / SYNCED_STANCES_DIR

def get_synced_module_path(ref: SourcedResource) -> Path:
    ref = SourceResolver.instance().dealias(ref)
    return (_modules_path() / ref.source.cache_subpath() / ref.path).with_suffix(".md")

def get_synced_stance_path(ref: SourcedResource) -> Path:
    ref = SourceResolver.instance().dealias(ref)
    return (_stances_path() / ref.source.cache_subpath() / ref.path).with_suffix(".yaml")

def create_synced_stances_dir():
    _stances_path().mkdir(parents=True, exist_ok=True)

def create_synced_modules_dir():
    _modules_path().mkdir(parents=True, exist_ok=True)

def read_synced_module(ref: SourcedResource) -> Module:
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_module_path(ref)
    return Module.load(file_path.read_text())

def write_synced_module(ref: SourcedResource, module: Module):
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_module_path(ref)
    content = module.dump()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

def remove_synced_module(ref: SourcedResource):
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_module_path(ref)
    if file_path.exists():
        file_path.unlink(missing_ok=True)

def read_synced_stance(ref: SourcedResource) -> Stance:
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_stance_path(ref)
    return Stance.load(file_path.read_text())

def write_synced_stance(ref: SourcedResource, stance: Stance):
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_stance_path(ref)
    content = stance.dump()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

def remove_synced_stance(ref: SourcedResource):
    ref = SourceResolver.instance().dealias(ref)
    file_path = get_synced_stance_path(ref)
    if file_path.exists():
        file_path.unlink(missing_ok=True)

def _rel_to_resource(base: Path, src: Path) -> SourcedResource:
    parts = src.relative_to(base).with_suffix("").parts
    return SourcedResource(SourceReference.from_cache_subpath(parts[0], parts[1]), path="/".join(parts[2:]))

def list_synced_modules() -> list[SourcedResource]:
    p = _modules_path()
    if not p.exists():
        return []
    return sorted(
        (_rel_to_resource(p, src) for src in p.rglob("*.md")),
        key=lambda r: (r.source.scheme, r.source.address, r.path),
    )

def list_synced_stances() -> list[SourcedResource]:
    p = _stances_path()
    if not p.exists():
        return []
    return sorted(
        (_rel_to_resource(p, src) for src in p.rglob("*.yaml")),
        key=lambda r: (r.source.scheme, r.source.address, r.path),
    )
