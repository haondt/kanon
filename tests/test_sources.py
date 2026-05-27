from __future__ import annotations

from pathlib import Path

import pytest

from spek.core.sources import (
    GitHubSource,
    GitLabSource,
    LocalSource,
    parse_source_ref,
)


def test_parse_local_absolute(tmp_path):
    result = parse_source_ref(str(tmp_path))
    assert isinstance(result, LocalSource)
    assert result.root == tmp_path


def test_parse_local_tilde(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    result = parse_source_ref("~/specs")
    assert isinstance(result, LocalSource)
    assert result.root == tmp_path / "specs"


def test_parse_github_simple():
    result = parse_source_ref("gh::org/repo")
    assert isinstance(result, GitHubSource)
    assert result.org == "org"
    assert result.repo == "repo"
    assert result.ref is None


def test_parse_github_with_ref():
    result = parse_source_ref("gh::org/repo@main")
    assert isinstance(result, GitHubSource)
    assert result.ref == "main"


def test_parse_github_invalid_missing_repo():
    with pytest.raises(ValueError):
        parse_source_ref("gh::org")


def test_parse_github_invalid_too_many_segments():
    with pytest.raises(ValueError):
        parse_source_ref("gh::org/group/repo")


def test_parse_gitlab_simple():
    result = parse_source_ref("gl::group/repo")
    assert isinstance(result, GitLabSource)
    assert result.groups == ["group"]
    assert result.repo == "repo"
    assert result.ref is None


def test_parse_gitlab_nested():
    result = parse_source_ref("gl::group/subgroup/repo@v1")
    assert isinstance(result, GitLabSource)
    assert result.groups == ["group", "subgroup"]
    assert result.repo == "repo"
    assert result.ref == "v1"


def test_parse_gitlab_invalid_single_segment():
    with pytest.raises(ValueError):
        parse_source_ref("gl::repo")
