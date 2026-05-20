from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from spek.core.yaml_utils import load_yaml


class ProfileSpec(BaseModel):
    description: str = ""
    extends: list[str] = []
    modules: list[str] = []
    stances: list[str] = []


def resolve_profile(
    name: str,
    profiles_dir: Path,
    _seen: frozenset[str] = frozenset(),
) -> tuple[list[str], list[str]]:
    """Recursively resolve a profile to (modules, stances) lists.

    Lists from extended profiles come first; the current profile appends after.
    Raises ValueError on circular dependencies.
    """
    if name in _seen:
        raise ValueError(f"Circular profile dependency: {name}")

    profile_file = profiles_dir / (name + ".yaml")
    if not profile_file.exists():
        raise FileNotFoundError(f"Profile '{name}' not found at {profile_file}")

    spec = load_yaml(profile_file, ProfileSpec)
    seen = _seen | {name}
    modules: list[str] = []
    stances: list[str] = []

    for parent in spec.extends:
        parent_modules, parent_stances = resolve_profile(parent, profiles_dir, seen)
        for m in parent_modules:
            if m not in modules:
                modules.append(m)
        for s in parent_stances:
            if s not in stances:
                stances.append(s)

    for m in spec.modules:
        if m not in modules:
            modules.append(m)

    for s in spec.stances:
        if s not in stances:
            stances.append(s)

    return modules, stances


def list_profiles(profiles_dir: Path) -> dict[str, str]:
    """Return {profile_name: description} for all profiles, sorted."""
    if not profiles_dir.exists():
        return {}
    return {
        str(f.relative_to(profiles_dir).with_suffix("")): load_yaml(f, ProfileSpec).description
        for f in sorted(profiles_dir.rglob("*.yaml"))
    }
