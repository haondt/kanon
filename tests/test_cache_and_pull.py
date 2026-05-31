"""Tests for gh::/gl:: source caching, kanon source pull, and kanon cache clear/status."""
from __future__ import annotations

import shutil
import types
from pathlib import Path
from unittest.mock import MagicMock

import git
import pytest
import yaml
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import (
    GITHUB_SCHEME,
    GITLAB_SCHEME,
    SOURCED_KANONS_DIR,
    SourceReference,
    SourcedResource,
    KanonConfig,
    KanonEnv,
)
from kanon.core.sources import GitHubSource, GitLabSource
from kanon.core.sources._base import ParsedSource, PullResult


# ── helpers ───────────────────────────────────────────────────────────────────


def make_bare_repo(path: Path) -> git.Repo:
    """Create a real bare git repo with one commit so it can be cloned."""
    work = path.parent / (path.name + "_work")
    work.mkdir()
    repo = git.Repo.init(str(work))
    repo.config_writer().set_value("user", "name", "test").release()
    repo.config_writer().set_value("user", "email", "test@test.com").release()
    (work / "README.md").write_text("hello")
    repo.index.add(["README.md"])
    repo.index.commit("init")
    bare = git.Repo.clone_from(str(work), str(path), bare=True)
    shutil.rmtree(str(work))
    return bare


def make_config(root: Path, **extra) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": [],
        **extra,
    }))


# ── cache_path() derivation ───────────────────────────────────────────────────


def test_cache_path_gh_no_ref(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    src = GitHubSource.parse("org/repo")
    assert src.cache_path() == tmp_path / "cache" / GITHUB_SCHEME / "org%2Frepo"


def test_cache_path_gh_with_ref(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    src = GitHubSource.parse("org/repo@main")
    assert src.cache_path() == tmp_path / "cache" / GITHUB_SCHEME / "org%2Frepo%40main"


def test_cache_path_gl_groups(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    src = GitLabSource.parse("g1/g2/repo@abc")
    assert src.cache_path() == tmp_path / "cache" / GITLAB_SCHEME / "g1%2Fg2%2Frepo%40abc"


# ── pull() behaviour ──────────────────────────────────────────────────────────


def test_pull_clones_when_missing(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    make_bare_repo(remote)
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    src = GitHubSource.parse("org/repo")

    def _patched_ensure_cloned(self):
        path = self.cache_path()
        if not (path / ".git").exists():
            git.Repo.clone_from(str(remote), str(path))
        return path

    src._ensure_cloned = types.MethodType(_patched_ensure_cloned, src)
    result = src.pull()
    assert result == PullResult.CLONED
    assert src.cache_path().exists()


def test_pull_noop_when_present_force_false(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    make_bare_repo(remote)
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    src = GitHubSource.parse( "org/repo")  # type: ignore[arg-type]
    cache_path = src.cache_path()
    # Pre-clone so cache already exists
    git.Repo.clone_from(str(remote), str(cache_path))

    def _patched_ensure_cloned(self):
        return self.cache_path()

    src._ensure_cloned = types.MethodType(_patched_ensure_cloned, src)
    result = src.pull(force=False)
    assert result == PullResult.CACHED


def test_pull_fetches_when_present_force_true(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    make_bare_repo(remote)
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    src = GitHubSource.parse("org/repo")
    cache_path = src.cache_path()
    git.Repo.clone_from(str(remote), str(cache_path))

    def _patched_ensure_cloned(self):
        return self.cache_path()

    src._ensure_cloned = types.MethodType(_patched_ensure_cloned, src)
    result = src.pull(force=True)
    assert result == PullResult.PULLED


# ── kanon source pull CLI ──────────────────────────────────────────────────────


def test_source_pull_no_args(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "pull"])
    assert result.exit_code == 0, result.output


def test_source_pull_by_alias(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    local_src = tmp_path / "ext"
    local_src.mkdir()
    make_config(tmp_path, sources={"mywork": f"local::{local_src}"})

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "pull", "mywork"])
    assert result.exit_code == 0, result.output


def test_source_pull_unknown_name(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "pull", "alias::doesnotexist"])
    assert result.exit_code != 0


def test_source_pull_by_direct_ref(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    make_config(tmp_path)

    cloned = []

    def fake_clone_from(url, path, **kwargs):
        Path(path).mkdir(parents=True, exist_ok=True)
        cloned.append(path)
        return MagicMock()

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(fake_clone_from))

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "pull", "gh::org/repo"])
    assert result.exit_code == 0, result.output
    assert cloned


# ── kanon cache clear CLI ──────────────────────────────────────────────────────


def test_cache_clear_all(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "gh" / "org" / "repo").mkdir(parents=True)
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "cache", "clear"])
    assert result.exit_code == 0, result.output
    assert not cache_dir.exists()


def test_cache_clear_named(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    remote = tmp_path / "remote.git"
    make_bare_repo(remote)

    cache_dir = tmp_path / "cache"
    src_cache = cache_dir / GITHUB_SCHEME / "org%2Frepo"
    git.Repo.clone_from(str(remote), str(src_cache))

    other = cache_dir / GITHUB_SCHEME / "org%2Fother"
    git.Repo.clone_from(str(remote), str(other))

    make_config(tmp_path, sources={"mywork": "gh::org/repo"})

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "cache", "clear", "mywork"])
    assert result.exit_code == 0, result.output
    assert not src_cache.exists()
    assert other.exists()


def test_cache_clear_named_no_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    local_src = tmp_path / "ext"
    local_src.mkdir()
    make_config(tmp_path, sources={"mywork": f"local::{local_src}"})

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "cache", "clear", "mywork"])
    assert result.exit_code == 0, result.output
    assert "no cache" in result.output


# ── kanon sync --pull calls pull on all sources ────────────────────────────────


def test_sync_pull_calls_pull_on_all_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    ext_dir = tmp_path / "ext"
    ext_dir.mkdir()
    (ext_dir / "kanons" / "python").mkdir(parents=True)
    (ext_dir / "kanons" / "python" / "style.md").write_text("Style rule.")

    make_config(tmp_path, sources={"mywork": f"local::{ext_dir}"}, kanons=["mywork::python/style"])

    kanon_dir = tmp_path / ".kanon"
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()

    pulled_sources: list[tuple[object, bool]] = []

    original_pull = ParsedSource.pull

    def tracking_pull(self, force=False):
        pulled_sources.append((self, force))
        return original_pull(self, force=force)

    monkeypatch.setattr(ParsedSource, "pull", tracking_pull)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync", "--pull"])
    assert result.exit_code == 0, result.output
    assert any(force for _, force in pulled_sources)


# ── kanon source add clones remote ─────────────────────────────────────────────


def test_source_add_clones_remote(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    make_config(tmp_path)

    remote = tmp_path / "remote.git"
    make_bare_repo(remote)

    pull_called = []

    def _patched_ensure_cloned(self):
        path = self.cache_path()
        if not (path / ".git").exists():
            git.Repo.clone_from(str(remote), str(path))
            pull_called.append(True)
        return path

    monkeypatch.setattr(GitHubSource, "_ensure_cloned", _patched_ensure_cloned)

    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "upstream", "gh::org/repo",
    ])
    assert result.exit_code == 0, result.output
    assert pull_called


# ── kanon add clones remote source ───────────────────────────────────────────


def test_kanon_add_clones_remote_source(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()

    cache_path = tmp_path / "cache" / GITHUB_SCHEME / "org%2Frepo"
    cloned = []

    def fake_clone_from(url, path, **kwargs):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        (p / ".git").mkdir()
        kanons_dir = p / SOURCED_KANONS_DIR / "python"
        kanons_dir.mkdir(parents=True)
        (kanons_dir / "style.md").write_text("Style rule.")
        cloned.append(path)
        return MagicMock()

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(fake_clone_from))

    make_config(tmp_path, sources={"upstream": "gh::org/repo"})
    kanon_dir = tmp_path / ".kanon"
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "add", "upstream::python/style",
    ])
    assert result.exit_code == 0, result.output
    assert cloned
    assert cache_path.exists()


# ── kanon cache status ─────────────────────────────────────────────────────────


def test_cache_status_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "cache", "status"])
    assert result.exit_code == 0, result.output
    assert "empty" in result.output.lower()


def test_cache_status_shows_cloned_repo(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SOURCES_CACHE_PATH", str(tmp_path / "cache"))
    KanonEnv.reset()
    remote = tmp_path / "remote.git"
    make_bare_repo(remote)
    repo_path = tmp_path / "cache" / "gh" / "org%2Frepo"
    git.Repo.clone_from(str(remote), str(repo_path))
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "cache", "status"])
    assert result.exit_code == 0, result.output
    assert "gh" in result.output
    assert "org%2Frepo" in result.output


# ── list_synced_kanons round-trip ─────────────────────────────────────────────


def _make_kanon_dir(root: Path) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanons").mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": [],
    }))


def test_list_synced_kanons_roundtrip_gh_source(tmp_path):
    from kanon.commands.sync._synced import list_synced_kanons, write_synced_kanon
    from kanon.core.kanons import Kanon
    _make_kanon_dir(tmp_path)
    KanonConfig.initialize(tmp_path)

    resource = SourcedResource(SourceReference("gh", "org/repo"), "python/style")
    write_synced_kanon(resource, Kanon.load("Style rule."))

    assert resource in list_synced_kanons()


def test_list_synced_kanons_roundtrip_local_absolute_path(tmp_path):
    from kanon.commands.sync._synced import list_synced_kanons, write_synced_kanon
    from kanon.core.kanons import Kanon
    _make_kanon_dir(tmp_path)
    KanonConfig.initialize(tmp_path)

    resource = SourcedResource(SourceReference("local", "/home/user/my-kanons"), "python/style")
    write_synced_kanon(resource, Kanon.load("Style rule."))

    assert resource in list_synced_kanons()


def test_list_synced_kanons_roundtrip_gl_with_groups(tmp_path):
    from kanon.commands.sync._synced import list_synced_kanons, write_synced_kanon
    from kanon.core.kanons import Kanon
    _make_kanon_dir(tmp_path)
    KanonConfig.initialize(tmp_path)

    resource = SourcedResource(SourceReference("gl", "group/subgroup/repo@main"), "conventions/commits")
    write_synced_kanon(resource, Kanon.load("Commit rule."))

    assert resource in list_synced_kanons()
