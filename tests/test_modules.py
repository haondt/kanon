from __future__ import annotations

import pytest
from pathlib import Path

from spek.core.modules import list_modules, parse_module_ref, resolve_sources
from spek.core.settings import SourceSpec


def test_parse_module_ref_bare_defaults_to_spek():
    assert parse_module_ref("git/commit-base") == ("spek", "git/commit-base")


def test_parse_module_ref_with_namespace():
    assert parse_module_ref("mywork::python/style") == ("mywork", "python/style")


def test_parse_module_ref_namespace_only_bare():
    assert parse_module_ref("corp::single") == ("corp", "single")


def test_parse_module_ref_deep_path():
    assert parse_module_ref("ns::a/b/c") == ("ns", "a/b/c")


def test_resolve_sources_spek_always_injected(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    sources = resolve_sources(repo_path, {}, {})
    assert "spek" in sources
    assert sources["spek"] == repo_path / "specs"


def test_resolve_sources_project_wins_over_global(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    global_sources = {"mywork": SourceSpec(path="/global/path")}
    project_sources = {"mywork": SourceSpec(path="/project/path")}
    sources = resolve_sources(repo_path, global_sources, project_sources)
    assert sources["mywork"] == Path("/project/path")


def test_resolve_sources_global_included_when_no_project_override(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    global_sources = {"corp": SourceSpec(path="/corp/specs")}
    sources = resolve_sources(repo_path, global_sources, {})
    assert "corp" in sources
    assert sources["corp"] == Path("/corp/specs")


def test_resolve_sources_allows_spek_override_in_global(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    sources = resolve_sources(repo_path, {"spek": SourceSpec(path="/custom/specs")}, {})
    assert sources["spek"] == Path("/custom/specs")


def test_resolve_sources_allows_spek_override_in_project(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    sources = resolve_sources(repo_path, {}, {"spek": SourceSpec(path="/fork/specs")})
    assert sources["spek"] == Path("/fork/specs")


def test_resolve_sources_project_spek_beats_global_spek(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    sources = resolve_sources(
        repo_path,
        {"spek": SourceSpec(path="/global/specs")},
        {"spek": SourceSpec(path="/project/specs")},
    )
    assert sources["spek"] == Path("/project/specs")


def test_resolve_sources_no_repo_path_omits_spek_when_not_configured():
    sources = resolve_sources(None, {}, {})
    assert "spek" not in sources


def test_resolve_sources_no_repo_path_uses_configured_spek():
    sources = resolve_sources(None, {}, {"spek": SourceSpec(path="/my/specs")})
    assert sources["spek"] == Path("/my/specs")


def test_list_modules_returns_sorted_names(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "a").mkdir()
    (specs / "b").mkdir()
    (specs / "a" / "foo.md").write_text("")
    (specs / "b" / "bar.md").write_text("")
    result = list_modules(specs)
    assert result == ["a/foo", "b/bar"]


def test_list_modules_deduplicates_md_and_yaml(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "x.md").write_text("")
    (specs / "x.yaml").write_text("")
    result = list_modules(specs)
    assert result.count("x") == 1
