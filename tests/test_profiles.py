from pathlib import Path

import pytest
import yaml

from spek.core.config import LOCAL_SCHEME, SourceReference, SourcedResource
from spek.core.profiles import ProfileSpec


def write_profile(profiles_dir: Path, name: str, **fields) -> None:
    path = profiles_dir / (name + ".yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(fields))


def make_factory(profiles_dir: Path):
    def factory(res: SourcedResource) -> str:
        return (profiles_dir / (res.path + ".yaml")).read_text()
    return factory


def test_resolve_profile_inheritance(tmp_path: Path):
    write_profile(tmp_path, "base", modules=["tools/spek/module", "tools/spek/session"])
    write_profile(tmp_path, "source", extends=["base"], modules=["tools/spek/source", "tools/spek/session"])

    content = (tmp_path / "source.yaml").read_text()
    profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "source")
    result = ProfileSpec.load(content, make_factory(tmp_path), profile_res.source, frozenset({profile_res}))

    assert set(result.modules) == {"tools/spek/module", "tools/spek/session", "tools/spek/source"}
    assert result.stances == []


def test_resolve_profile_stances(tmp_path: Path):
    write_profile(tmp_path, "base", stances=["autonomous"])
    write_profile(tmp_path, "child", extends=["base"], stances=["collaborative", "autonomous"])

    content = (tmp_path / "child.yaml").read_text()
    profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "child")
    result = ProfileSpec.load(content, make_factory(tmp_path), profile_res.source, frozenset({profile_res}))

    assert set(result.stances) == {"autonomous", "collaborative"}


def test_resolve_profile_circular_raises(tmp_path: Path):
    write_profile(tmp_path, "a", extends=["b"])
    write_profile(tmp_path, "b", extends=["a"])

    content = (tmp_path / "a.yaml").read_text()
    with pytest.raises(ValueError, match="Circular"):
        profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "a")
        ProfileSpec.load(content, make_factory(tmp_path), profile_res.source, frozenset({profile_res}))


def test_resolve_profile_missing_raises(tmp_path: Path):
    content = yaml.dump({"extends": ["nonexistent"]})
    with pytest.raises(FileNotFoundError):
        profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "root")
        ProfileSpec.load(content, make_factory(tmp_path), profile_res.source, frozenset({profile_res}))
