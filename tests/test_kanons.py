from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from kanon.core.config import KanonConfig, SourcedResource, SourceReference, KanonEnv
from kanon.core.sources._local import LocalSource
from kanon.core.sources._resolve import resolve_sources


# ── SourcedResource.parse ─────────────────────────────────────────────────────


def test_parse_bare_defaults_to_kanon():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.source.scheme == "kanon"
    assert sr.source.address == "kanon"
    assert sr.path == "git/commit-base"
    assert sr.as_string == "git/commit-base"


def test_parse_builtin_shorthand_project():
    sr = SourcedResource.parse("project::python/style")
    assert sr.source.scheme == "kanon"
    assert sr.source.address == "project"
    assert sr.path == "python/style"
    assert sr.as_string == "project::python/style"


def test_parse_builtin_shorthand_self():
    sr = SourcedResource.parse("self::python/style")
    assert sr.source.scheme == "kanon"
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


# ── SourcedResource args ──────────────────────────────────────────────────────


def test_parse_args_flag():
    sr = SourcedResource.parse("foo/bar[baz]")
    assert sr.path == "foo/bar"
    assert sr.args == {"baz": True}


def test_parse_args_key_value():
    sr = SourcedResource.parse("foo/bar[baz=qux]")
    assert sr.path == "foo/bar"
    assert sr.args == {"baz": "qux"}


def test_parse_args_multiple():
    sr = SourcedResource.parse("foo/bar[baz,qux=corge]")
    assert sr.path == "foo/bar"
    assert sr.args == {"baz": True, "qux": "corge"}


def test_parse_args_with_source_prefix():
    sr = SourcedResource.parse("gh::org/repo::foo/bar[baz=qux]")
    assert sr.source.scheme == "gh"
    assert sr.path == "foo/bar"
    assert sr.args == {"baz": "qux"}


def test_parse_args_no_args_is_empty_dict():
    sr = SourcedResource.parse("foo/bar")
    assert sr.args == {}


def test_as_string_with_flag_arg():
    sr = SourcedResource.parse("foo/bar[baz]")
    assert sr.as_string == "foo/bar[baz]"


def test_as_string_with_key_value_arg():
    sr = SourcedResource.parse("gh::org/repo::foo/bar[baz=qux]")
    assert sr.as_string == "gh::org/repo::foo/bar[baz=qux]"


def test_as_path_string_excludes_args():
    sr = SourcedResource.parse("foo/bar[baz]")
    assert sr.as_path_string == "kanon::kanon::foo/bar"


def test_as_fully_qualified_string_includes_args():
    sr = SourcedResource.parse("foo/bar[baz]")
    assert sr.as_fully_qualified_string == "kanon::kanon::foo/bar[baz]"


def test_args_included_in_identity():
    a = SourcedResource.parse("foo/bar[baz]")
    b = SourcedResource.parse("foo/bar")
    assert a != b
    assert hash(a) != hash(b)


def test_same_args_equal():
    a = SourcedResource.parse("foo/bar[baz]")
    b = SourcedResource.parse("foo/bar[baz]")
    assert a == b
    assert hash(a) == hash(b)


def test_as_string_kanon_kanon_is_bare():
    sr = SourcedResource(SourceReference("kanon", "kanon"), "git/commit-base")
    assert sr.as_string == "git/commit-base"


def test_as_string_kanon_project_is_two_part():
    sr = SourcedResource(SourceReference("kanon", "project"), "my/kanon")
    assert sr.as_string == "project::my/kanon"


def test_as_string_alias_is_two_part():
    sr = SourcedResource(SourceReference("alias", "mywork"), "python/style")
    assert sr.as_string == "mywork::python/style"


def test_as_string_gh_is_fully_qualified():
    sr = SourcedResource(SourceReference("gh", "org/repo"), "python/style")
    assert sr.as_string == "gh::org/repo::python/style"


def test_as_fully_qualified_string():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.as_fully_qualified_string == "kanon::kanon::git/commit-base"


def test_source_key_kanon():
    sr = SourcedResource.parse("git/commit-base")
    assert sr.source == SourceReference.KANON_SOURCE_REFERENCE


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


def _make_kanon_yaml(kanon_dir: Path, sources: dict | None = None) -> None:
    data: dict = {
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": [],
    }
    if sources:
        data["sources"] = sources
    (kanon_dir / "kanon.yaml").write_text(yaml.dump(data))


def test_resolve_sources_kanon_always_present(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    _make_kanon_yaml(kanon_dir)
    KanonConfig.initialize(tmp_path)
    sources = resolve_sources()
    assert SourceReference.KANON_SOURCE_REFERENCE in sources


def test_resolve_sources_project_source_when_config_loaded(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    _make_kanon_yaml(kanon_dir)
    KanonConfig.initialize(tmp_path)
    sources = resolve_sources()
    assert SourceReference.PROJECT_SOURCE_REFERENCE in sources


def test_resolve_sources_project_source_wins_over_global(tmp_path, monkeypatch):
    global_src = tmp_path / "global-src"
    global_src.mkdir()
    project_src = tmp_path / "project-src"
    project_src.mkdir()

    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    _make_kanon_yaml(kanon_dir, sources={"mywork": str(project_src)})
    KanonConfig.initialize(tmp_path)

    settings_path = kanon_dir / "settings.yaml"
    settings_path.write_text(yaml.dump({"sources": {"mywork": str(global_src)}}))
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(settings_path))
    KanonEnv.reset()

    sources = resolve_sources()
    assert sources[SourceReference("alias", "mywork")].root == project_src  # type: ignore[attr-defined]


def test_resolve_sources_global_included_when_no_project_override(tmp_path, monkeypatch):
    corp_src = tmp_path / "corp-src"
    corp_src.mkdir()

    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    _make_kanon_yaml(kanon_dir)
    KanonConfig.initialize(tmp_path)

    settings_path = kanon_dir / "settings.yaml"
    settings_path.write_text(yaml.dump({"sources": {"corp": str(corp_src)}}))
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(settings_path))
    KanonEnv.reset()

    sources = resolve_sources()
    assert SourceReference("alias", "corp") in sources


# ── LocalSource.list_kanons ──────────────────────────────────────────────────


def test_list_kanons_returns_sorted_names(tmp_path):
    kanons = tmp_path / "kanons"
    kanons.mkdir()
    (kanons / "a").mkdir()
    (kanons / "b").mkdir()
    (kanons / "a" / "foo.md").write_text("")
    (kanons / "b" / "bar.md").write_text("")
    source = LocalSource(original_address=str(tmp_path), root=tmp_path)
    result = source.list_kanons()
    assert result == ["a/foo", "b/bar"]


def test_list_kanons_ignores_non_md_files(tmp_path):
    kanons = tmp_path / "kanons"
    kanons.mkdir()
    (kanons / "x.md").write_text("")
    (kanons / "x.yaml").write_text("")
    source = LocalSource(original_address=str(tmp_path), root=tmp_path)
    result = source.list_kanons()
    assert result == ["x"]


def test_list_kanons_empty_when_no_kanons_dir(tmp_path):
    source = LocalSource(original_address=str(tmp_path), root=tmp_path)
    result = source.list_kanons()
    assert result == []
