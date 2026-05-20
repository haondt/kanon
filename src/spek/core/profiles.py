from __future__ import annotations

import yaml
from pathlib import Path


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

    data = yaml.safe_load(profile_file.read_text()) or {}
    seen = _seen | {name}
    modules: list[str] = []
    stances: list[str] = []

    for parent in data.get("extends", []):
        parent_modules, parent_stances = resolve_profile(parent, profiles_dir, seen)
        for m in parent_modules:
            if m not in modules:
                modules.append(m)
        for s in parent_stances:
            if s not in stances:
                stances.append(s)

    for m in data.get("modules", []):
        if m not in modules:
            modules.append(m)

    for s in data.get("stances", []):
        if s not in stances:
            stances.append(s)

    return modules, stances


def list_profiles(profiles_dir: Path) -> dict[str, str]:
    """Return {profile_name: description} for all profiles, sorted."""
    result: dict[str, str] = {}
    if not profiles_dir.exists():
        return result
    for f in sorted(profiles_dir.rglob("*.yaml")):
        key = str(f.relative_to(profiles_dir).with_suffix(""))
        data = yaml.safe_load(f.read_text()) or {}
        result[key] = data.get("description", "")
    return result
