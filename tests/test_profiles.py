from pathlib import Path

import pytest
import yaml

from spek.core.profiles import ProfileSpec


def write_profile(profiles_dir: Path, name: str, **fields) -> None:
    path = profiles_dir / (name + ".yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(fields))


def make_factory(profiles_dir: Path):
    def factory(name: str) -> str:
        return (profiles_dir / (name + ".yaml")).read_text()
    return factory


def test_resolve_profile_inheritance(tmp_path):
    write_profile(tmp_path, "base", modules=["git/commit-style", "docs/readme"])
    write_profile(tmp_path, "python", extends=["base"], modules=["python/style", "docs/readme"])

    content = (tmp_path / "python.yaml").read_text()
    result = ProfileSpec.load(content, make_factory(tmp_path), frozenset({"python"}))

    assert set(result.modules) == {"git/commit-style", "docs/readme", "python/style"}
    assert result.stances == []


def test_resolve_profile_stances(tmp_path):
    write_profile(tmp_path, "base", stances=["autonomous"])
    write_profile(tmp_path, "child", extends=["base"], stances=["collaborative", "autonomous"])

    content = (tmp_path / "child.yaml").read_text()
    result = ProfileSpec.load(content, make_factory(tmp_path), frozenset({"child"}))

    assert set(result.stances) == {"autonomous", "collaborative"}


def test_resolve_profile_circular_raises(tmp_path):
    write_profile(tmp_path, "a", extends=["b"])
    write_profile(tmp_path, "b", extends=["a"])

    content = (tmp_path / "a.yaml").read_text()
    with pytest.raises(ValueError, match="Circular"):
        ProfileSpec.load(content, make_factory(tmp_path), frozenset({"a"}))


def test_resolve_profile_missing_raises(tmp_path):
    content = yaml.dump({"extends": ["nonexistent"]})
    with pytest.raises(FileNotFoundError):
        ProfileSpec.load(content, make_factory(tmp_path), frozenset({"root"}))
