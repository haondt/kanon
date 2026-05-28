from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from spek.core.config import SpekConfig, SourcedResource, SourceReference, SpekEnv
from spek.core.settings import GlobalSettings
from spek.core.sources._local import LocalSource
from spek.core.sources._resolve import resolve_sources, _resolver


# ── SourcedResource.parse ─────────────────────────────────────────────────────


def test_parse_bare_defaults_to_spek():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.source.scheme == "spek"
    assert sr.source.address == "spek"
    assert sr.path == "git/commit-base"
    assert sr.as_string == "git/commit-base"


def test_parse_builtin_shorthand_project():
    sr = SourcedResource.parse("project::python/style")
    assert sr.source.scheme == "spek"
    assert sr.source.address == "project"
    assert sr.path == "python/style"
    assert sr.as_string == "project::python/style"


def test_parse_builtin_shorthand_self():
    sr = SourcedResource.parse("self::python/style")
    assert sr.source.scheme == "spek"
    assert sr.source.address == "self"
    assert sr.path == "python/style"
    assert sr.as_string == "self::python/style"


def test_parse_two_part_alias():
    sr = SourcedResource.parse("mywork::python/style")
    assert sr.source.scheme == "alias"
    assert sr.source.address == "mywork"
    assert sr.path == "python/style"
    assert sr.as_string == "mywork::python/style"


def test_parse_two_part_alias_bare():
    sr = SourcedResource.parse("corp::single")
    assert sr.source.scheme == "alias"
    assert sr.source.address == "corp"
    assert sr.path == "single"


def test_parse_deep_alias_path():
    sr = SourcedResource.parse("ns::a/b/c")
    assert sr.source.scheme == "alias"
    assert sr.source.address == "ns"
    assert sr.path == "a/b/c"


def test_parse_three_part_gh():
    sr = SourcedResource.parse("gh::org/repo::python/style")
    assert sr.source.scheme == "gh"
    assert sr.source.address == "org/repo"
    assert sr.path == "python/style"
    assert sr.as_fully_qualified_string == "gh::org/repo::python/style"


def test_parse_three_part_local():
    sr = SourcedResource.parse("local::/some/path::python/style")
    assert sr.source.scheme == "local"
    assert sr.source.address == "/some/path"
    assert sr.path == "python/style"


def test_parse_too_many_separators_raises():
    with pytest.raises(ValueError):
        SourcedResource.parse("a::b::c::d")


def test_as_string_spek_spek_is_bare():
    sr = SourcedResource(SourceReference("spek", "spek"), "git/commit-base")
    assert sr.as_string == "git/commit-base"


def test_as_string_spek_project_is_two_part():
    sr = SourcedResource(SourceReference("spek", "project"), "my/module")
    assert sr.as_string == "project::my/module"


def test_as_string_alias_is_two_part():
    sr = SourcedResource(SourceReference("alias", "mywork"), "python/style")
    assert sr.as_string == "mywork::python/style"


def test_as_string_gh_is_fully_qualified():
    sr = SourcedResource(SourceReference("gh", "org/repo"), "python/style")
    assert sr.as_string == "gh::org/repo::python/style"


def test_as_fully_qualified_string():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.as_fully_qualified_string == "spek::spek::git/commit-base"


def test_source_key_spek():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.source == SourceReference.SPEK_SOURCE_REFERENCE


def test_source_key_alias():
    sr = SourcedResource.parse("mywork::python/style")
    assert sr.source == SourceReference("alias", "mywork")


def test_from_source_key():
    sr = SourcedResource(SourceReference.parse("alias::mywork", validate_as_key=True), "python/style")
    assert sr.source.scheme == "alias"
    assert sr.source.address == "mywork"
    assert sr.path == "python/style"


# ── resolve_sources ───────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clear_sources_cache():
    resolve_sources.cache_clear()
    yield
    resolve_sources.cache_clear()


def _make_spek_yaml(spek_dir: Path, sources: dict | None = None) -> None:
    data: dict = {
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": [],
    }
    if sources:
        data["sources"] = sources
    (spek_dir / "spek.yaml").write_text(yaml.dump(data))


def test_resolve_sources_spek_always_present(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_spek_yaml(spek_dir)
    SpekConfig.initialize(tmp_path)
    sources = resolve_sources()
    assert SourceReference.SPEK_SOURCE_REFERENCE in sources


def test_resolve_sources_project_source_when_config_loaded(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_spek_yaml(spek_dir)
    SpekConfig.initialize(tmp_path)
    sources = resolve_sources()
    assert SourceReference.PROJECT_SOURCE_REFERENCE in sources


def test_resolve_sources_project_source_wins_over_global(tmp_path, monkeypatch):
    global_src = tmp_path / "global-src"
    global_src.mkdir()
    project_src = tmp_path / "project-src"
    project_src.mkdir()

    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_spek_yaml(spek_dir, sources={"mywork": str(project_src)})
    SpekConfig.initialize(tmp_path)

    settings_path = spek_dir / "settings.yaml"
    settings_path.write_text(yaml.dump({"sources": {"mywork": str(global_src)}}))
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(settings_path))
    SpekEnv.reset()

    sources = resolve_sources()
    assert sources[SourceReference("alias", "mywork")].root == project_src  # type: ignore[attr-defined]


def test_resolve_sources_global_included_when_no_project_override(tmp_path, monkeypatch):
    corp_src = tmp_path / "corp-src"
    corp_src.mkdir()

    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    _make_spek_yaml(spek_dir)
    SpekConfig.initialize(tmp_path)

    settings_path = spek_dir / "settings.yaml"
    settings_path.write_text(yaml.dump({"sources": {"corp": str(corp_src)}}))
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(settings_path))
    SpekEnv.reset()

    sources = resolve_sources()
    assert SourceReference("alias", "corp") in sources


# ── LocalSource.list_modules ──────────────────────────────────────────────────


def test_list_modules_returns_sorted_names(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "a").mkdir()
    (specs / "b").mkdir()
    (specs / "a" / "foo.md").write_text("")
    (specs / "b" / "bar.md").write_text("")
    source = LocalSource(_resolver=_resolver, original_address=str(tmp_path), root=tmp_path)
    result = source.list_modules()
    assert result == ["a/foo", "b/bar"]


def test_list_modules_ignores_non_md_files(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "x.md").write_text("")
    (specs / "x.yaml").write_text("")
    source = LocalSource(_resolver=_resolver, original_address=str(tmp_path), root=tmp_path)
    result = source.list_modules()
    assert result == ["x"]


def test_list_modules_empty_when_no_specs_dir(tmp_path):
    source = LocalSource(_resolver=_resolver, original_address=str(tmp_path), root=tmp_path)
    result = source.list_modules()
    assert result == []
