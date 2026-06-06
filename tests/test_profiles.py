from pathlib import Path

import pytest
import yaml

from kanon.core.config import ALIAS_SCHEME, LOCAL_SCHEME, SourceReference, SourcedResource
from kanon.core.profiles import Profile


def write_profile(profiles_dir: Path, name: str, **fields) -> None:
    path = profiles_dir / (name + ".yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(fields))


def make_factory(profiles_dir: Path):
    def factory(res: SourcedResource) -> str:
        return (profiles_dir / (res.path + ".yaml")).read_text()
    return factory


def test_resolve_profile_inheritance(tmp_path: Path):
    write_profile(tmp_path, "base", kanons=["tools/kanon/kanons", "tools/kanon/session"])
    write_profile(tmp_path, "source", extends=["base"], kanons=["tools/kanon/source", "tools/kanon/session"])

    content = (tmp_path / "source.yaml").read_text()
    profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "source")
    result = Profile.load(content, make_factory(tmp_path), profile_res.source, lambda r: r, frozenset({profile_res}))

    assert set(result.kanons) == {"tools/kanon/kanons", "tools/kanon/session", "tools/kanon/source"}
    assert result.stances == []


def test_resolve_profile_stances(tmp_path: Path):
    write_profile(tmp_path, "base", stances=["autonomous"])
    write_profile(tmp_path, "child", extends=["base"], stances=["collaborative", "autonomous"])

    content = (tmp_path / "child.yaml").read_text()
    profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "child")
    result = Profile.load(content, make_factory(tmp_path), profile_res.source, lambda r: r, frozenset({profile_res}))

    assert set(result.stances) == {"autonomous", "collaborative"}


def test_resolve_profile_circular_raises(tmp_path: Path):
    write_profile(tmp_path, "a", extends=["b"])
    write_profile(tmp_path, "b", extends=["a"])

    content = (tmp_path / "a.yaml").read_text()
    with pytest.raises(ValueError, match="Circular"):
        profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "a")
        Profile.load(content, make_factory(tmp_path), profile_res.source, lambda r: r, frozenset({profile_res}))


def test_resolve_profile_self_extend_via_alias_circular_raises(tmp_path: Path):
    write_profile(tmp_path, "a", extends=["self::a"])

    content = (tmp_path / "a.yaml").read_text()
    resolved_source = SourceReference(LOCAL_SCHEME, str(tmp_path))
    alias_source = SourceReference(ALIAS_SCHEME, "mywork")
    seen = frozenset({SourcedResource(resolved_source, "a")})

    def dealias(r: SourcedResource) -> SourcedResource:
        if r.source == alias_source:
            return SourcedResource(resolved_source, r.path, r.args)
        return r

    with pytest.raises(ValueError, match="Circular"):
        Profile.load(content, make_factory(tmp_path), alias_source, dealias, seen)


def test_resolve_profile_missing_raises(tmp_path: Path):
    content = yaml.dump({"extends": ["nonexistent"]})
    with pytest.raises(FileNotFoundError):
        profile_res = SourcedResource(SourceReference(LOCAL_SCHEME, str(tmp_path)), "root")
        Profile.load(content, make_factory(tmp_path), profile_res.source, lambda r: r, frozenset({profile_res}))
