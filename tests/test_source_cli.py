from __future__ import annotations

import yaml
from click.testing import CliRunner
from pathlib import Path

from spek.cli import cli
from spek.core.config import SpekEnv
from spek.core.settings import GlobalSettings



def make_config(root: Path, **extra) -> None:
    spek_dir = root / ".spek"
    spek_dir.mkdir(exist_ok=True)
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": [],
        **extra,
    }))


# ── source add ────────────────────────────────────────────────────────────────


def test_source_add_local_writes_to_spek_yaml(tmp_path):
    make_config(tmp_path)
    src_dir = tmp_path / "my-specs"
    src_dir.mkdir()
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "mywork", str(src_dir),
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".spek" / "spek.yaml").read_text())
    assert "mywork" in raw["sources"]
    assert str(src_dir) in raw["sources"]["mywork"]


def test_source_add_expands_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "shared", "~/specs",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".spek" / "spek.yaml").read_text())
    assert "~/specs" in raw["sources"]["shared"]


def test_source_add_github_path_saved_as_is(tmp_path, monkeypatch):
    from spek.core.sources._github import GitHubSource
    monkeypatch.setattr(GitHubSource, "_ensure_cloned", lambda self: self.cache_path())
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "upstream", "gh::org/repo",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".spek" / "spek.yaml").read_text())
    assert raw["sources"]["upstream"] == "gh::org/repo"


def test_source_add_rejects_duplicate(tmp_path):
    make_config(tmp_path)
    src_dir = tmp_path / "specs"
    src_dir.mkdir()
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src_dir)])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src_dir)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_source_add_force_overwrites(tmp_path):
    make_config(tmp_path)
    src1 = tmp_path / "specs1"
    src1.mkdir()
    src2 = tmp_path / "specs2"
    src2.mkdir()
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src1)])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src2), "--force"])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".spek" / "spek.yaml").read_text())
    assert str(src2) in raw["sources"]["mywork"]


def test_source_add_global(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    src_dir = tmp_path / "shared"
    src_dir.mkdir()
    result = CliRunner().invoke(cli, ["source", "add", "--global", "corp", str(src_dir)])
    assert result.exit_code == 0, result.output
    settings = GlobalSettings.initialize()
    assert "corp" in settings.sources


def test_source_add_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "mywork", "/some/path",
    ])
    assert result.exit_code != 0
    assert "spek init" in result.output


# ── source remove ─────────────────────────────────────────────────────────────


def test_source_remove_deletes_source(tmp_path):
    make_config(tmp_path, sources={"mywork": "local::/some/path"})
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "remove", "mywork",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".spek" / "spek.yaml").read_text())
    assert "mywork" not in (raw.get("sources") or {})


def test_source_remove_missing_is_noop(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "remove", "nonexistent",
    ])
    assert result.exit_code == 0


# ── source status ─────────────────────────────────────────────────────────────


def test_source_status_shows_configured_sources(tmp_path):
    src_dir = tmp_path / "specs"
    src_dir.mkdir()
    make_config(tmp_path, sources={"mywork": f"local::{src_dir}"})
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "status"])
    assert result.exit_code == 0, result.output
    assert "mywork" in result.output


def test_source_status_no_user_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(tmp_path / ".spek" / "settings.yaml"))
    SpekEnv.reset()
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "status"])
    assert result.exit_code == 0
    assert "mywork" not in result.output
    assert "corp" not in result.output


# ── source add validation (Step 8) ────────────────────────────────────────────


def test_source_add_rejects_spek_project_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "spek::project", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_rejects_spek_self_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "spek::self", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_rejects_gh_prefixed_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "gh::mywork", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_allows_spek_spek_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "spek::spek", "/some/path",
    ])
    assert result.exit_code == 0, result.output
