from pathlib import Path

import pytest

from spek.core.profiles import resolve_profile


def write_profile(profiles_dir: Path, name: str, **fields) -> None:
    import yaml
    path = profiles_dir / (name + ".yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(fields))


def test_resolve_profile_inheritance(tmp_path):
    write_profile(tmp_path, "base", modules=["git/commit-style", "docs/readme"])
    write_profile(tmp_path, "python", extends=["base"], modules=["python/style", "docs/readme"])

    modules, stances = resolve_profile("python", tmp_path)

    # parent modules come first, child appends after, duplicate dropped
    assert modules == ["git/commit-style", "docs/readme", "python/style"]
    assert stances == []


def test_resolve_profile_stances(tmp_path):
    write_profile(tmp_path, "base", stances=["autonomous"])
    write_profile(tmp_path, "child", extends=["base"], stances=["collaborative", "autonomous"])

    _, stances = resolve_profile("child", tmp_path)

    assert stances == ["autonomous", "collaborative"]


def test_resolve_profile_circular_raises(tmp_path):
    write_profile(tmp_path, "a", extends=["b"])
    write_profile(tmp_path, "b", extends=["a"])

    with pytest.raises(ValueError, match="Circular"):
        resolve_profile("a", tmp_path)


def test_resolve_profile_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_profile("nonexistent", tmp_path)
