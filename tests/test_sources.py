from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spek.core.config import SpekConfig, SpekEnv, SourceReference
from spek.core.settings import GlobalSettings
from spek.core.sources import (
    AliasRef,
    GitHubSource,
    GitLabSource,
    LocalSource,
    hydrate_source_reference,
)
from spek.core.sources._resolve import resolve_sources


def test_parse_local_absolute(tmp_path):
    result = hydrate_source_reference(SourceReference("local", str(tmp_path)))
    assert isinstance(result, LocalSource)
    assert result.root == tmp_path


def test_parse_local_tilde(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    result = hydrate_source_reference(SourceReference("local", "~/specs"))
    assert isinstance(result, LocalSource)
    assert result.root == tmp_path / "specs"


def test_parse_github_simple():
    result = hydrate_source_reference(SourceReference("gh", "org/repo"))
    assert isinstance(result, GitHubSource)
    assert result.org == "org"
    assert result.repo == "repo"
    assert result.ref is None


def test_parse_github_with_ref():
    result = hydrate_source_reference(SourceReference("gh", "org/repo@main"))
    assert isinstance(result, GitHubSource)
    assert result.ref == "main"


def test_parse_github_invalid_missing_repo():
    with pytest.raises(ValueError):
        hydrate_source_reference(SourceReference("gh", "org"))


def test_parse_github_invalid_too_many_segments():
    with pytest.raises(ValueError):
        hydrate_source_reference(SourceReference("gh", "org/group/repo"))


def test_parse_gitlab_simple():
    result = hydrate_source_reference(SourceReference("gl", "group/repo"))
    assert isinstance(result, GitLabSource)
    assert result.groups == ["group"]
    assert result.repo == "repo"
    assert result.ref is None


def test_parse_gitlab_nested():
    result = hydrate_source_reference(SourceReference("gl", "group/subgroup/repo@v1"))
    assert isinstance(result, GitLabSource)
    assert result.groups == ["group", "subgroup"]
    assert result.repo == "repo"
    assert result.ref == "v1"


def test_parse_gitlab_invalid_single_segment():
    with pytest.raises(ValueError):
        hydrate_source_reference(SourceReference("gl", "repo"))


# ── SourceReference.parse ─────────────────────────────────────────────────────


def test_parse_bare_name():
    ref = SourceReference.parse("mywork")
    assert ref.scheme == "alias"
    assert ref.address == "mywork"


def test_parse_bare_absolute_path():
    ref = SourceReference.parse("/some/path")
    assert ref.scheme == "local"
    assert ref.address == "/some/path"


def test_parse_bare_tilde_path():
    ref = SourceReference.parse("~/specs")
    assert ref.scheme == "local"
    assert ref.address == "~/specs"


def test_parse_bare_relative_path():
    ref = SourceReference.parse("./specs")
    assert ref.scheme == "local"
    assert ref.address == "./specs"


def test_parse_alias_prefix():
    ref = SourceReference.parse("alias::mywork")
    assert ref.scheme == "alias"
    assert ref.address == "mywork"


def test_parse_local_prefix():
    ref = SourceReference.parse("local::foo/bar")
    assert ref.scheme == "local"
    assert ref.address == "foo/bar"


def test_parse_gh_prefix():
    ref = SourceReference.parse("gh::org/repo")
    assert ref.scheme == "gh"
    assert ref.address == "org/repo"


def test_parse_spek_spek():
    ref = SourceReference.parse("spek::spek")
    assert ref.scheme == "spek"
    assert ref.address == "spek"


# ── SourceReference.validate_as_key ───────────────────────────────────────────


def test_validate_as_key_bare_name():
    SourceReference.parse("mywork").validate_as_key()


def test_validate_as_key_alias_prefix():
    SourceReference.parse("alias::mywork").validate_as_key()


def test_validate_as_key_spek_spek_allowed():
    ref = SourceReference.parse("spek::spek")
    assert ref.scheme == "spek"
    assert ref.address == "spek"
    ref.validate_as_key()


def test_validate_as_key_spek_project_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("spek::project").validate_as_key()


def test_validate_as_key_spek_self_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("spek::self").validate_as_key()


def test_validate_as_key_spek_anything_else_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("spek::other").validate_as_key()


def test_validate_as_key_gh_prefix_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("gh::mywork").validate_as_key()


def test_validate_as_key_gl_prefix_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("gl::mywork").validate_as_key()


def test_validate_as_key_local_prefix_raises():
    with pytest.raises(ValueError):
        SourceReference.parse("local::mywork").validate_as_key()


# ── hydrate_source_reference ──────────────────────────────────────────────────


def test_hydrate_alias_ref():
    result = hydrate_source_reference(SourceReference("alias", "mywork"))
    assert isinstance(result, AliasRef)
    assert result.name == "mywork"


def test_hydrate_gh():
    result = hydrate_source_reference(SourceReference("gh", "org/repo"))
    assert isinstance(result, GitHubSource)
    assert result.org == "org"
    assert result.repo == "repo"


def test_hydrate_gl():
    result = hydrate_source_reference(SourceReference("gl", "group/repo"))
    assert isinstance(result, GitLabSource)


def test_hydrate_local_scheme(tmp_path):
    result = hydrate_source_reference(SourceReference("local", str(tmp_path)))
    assert isinstance(result, LocalSource)
    assert result.root == tmp_path


# ── resolve_sources cycle detection ───────────────────────────────────────────


@pytest.fixture(autouse=True)
def clear_resolve_cache():
    resolve_sources.cache_clear()
    GlobalSettings.reset()
    yield
    resolve_sources.cache_clear()
    GlobalSettings.reset()


def _make_config(spek_dir: Path, sources: dict | None = None) -> None:
    data: dict = {
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": [],
    }
    if sources:
        data["sources"] = sources
    (spek_dir / "spek.yaml").write_text(yaml.dump(data))


def test_resolve_sources_cycle_detection(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_config(spek_dir, sources={"a": "alias::b", "b": "alias::a"})
    SpekConfig.initialize(tmp_path)
    with pytest.raises(ValueError, match="Cycle"):
        resolve_sources()


def test_resolve_sources_indirect_cycle(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_config(spek_dir, sources={"a": "alias::b", "b": "alias::c", "c": "alias::a"})
    SpekConfig.initialize(tmp_path)
    with pytest.raises(ValueError, match="Cycle"):
        resolve_sources()


def test_resolve_sources_spek_spek_shadowing_warns(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_config(spek_dir, sources={"spek::spek": str(tmp_path)})
    SpekConfig.initialize(tmp_path)
    import warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolve_sources()
    assert any("shadowed" in str(w.message).lower() for w in caught)
