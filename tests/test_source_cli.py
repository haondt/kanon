from __future__ import annotations

import yaml
from click.testing import CliRunner
from pathlib import Path

from kanon.cli import cli
from kanon.core.config import KanonEnv
from kanon.core.settings import GlobalSettings



def make_config(root: Path, **extra) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": [],
        **extra,
    }))


# ── source add ────────────────────────────────────────────────────────────────


def test_source_add_local_writes_to_kanon_yaml(tmp_path):
    make_config(tmp_path)
    src_dir = tmp_path / "my-kanons"
    src_dir.mkdir()
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "mywork", str(src_dir),
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".kanon" / "kanon.yaml").read_text())
    assert "mywork" in raw["sources"]
    assert str(src_dir) in raw["sources"]["mywork"]


def test_source_add_expands_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "shared", "~/kanons",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".kanon" / "kanon.yaml").read_text())
    assert "~/kanons" in raw["sources"]["shared"]


def test_source_add_github_path_saved_as_is(tmp_path, monkeypatch):
    from kanon.core.sources._github import GitHubSource
    monkeypatch.setattr(GitHubSource, "_ensure_cloned", lambda self: self.cache_path())
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "upstream", "gh::org/repo",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".kanon" / "kanon.yaml").read_text())
    assert raw["sources"]["upstream"] == "gh::org/repo"


def test_source_add_rejects_duplicate(tmp_path):
    make_config(tmp_path)
    src_dir = tmp_path / "kanons"
    src_dir.mkdir()
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src_dir)])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src_dir)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_source_add_force_overwrites(tmp_path):
    make_config(tmp_path)
    src1 = tmp_path / "kanons1"
    src1.mkdir()
    src2 = tmp_path / "kanons2"
    src2.mkdir()
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src1)])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "add", "mywork", str(src2), "--force"])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".kanon" / "kanon.yaml").read_text())
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
    assert "kanon init" in result.output


# ── source remove ─────────────────────────────────────────────────────────────


def test_source_remove_deletes_source(tmp_path):
    make_config(tmp_path, sources={"mywork": "local::/some/path"})
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "remove", "mywork",
    ])
    assert result.exit_code == 0, result.output
    raw = yaml.safe_load((tmp_path / ".kanon" / "kanon.yaml").read_text())
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
    src_dir = tmp_path / "kanons"
    src_dir.mkdir()
    make_config(tmp_path, sources={"mywork": f"local::{src_dir}"})
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "status"])
    assert result.exit_code == 0, result.output
    assert "mywork" in result.output


def test_source_status_no_user_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(tmp_path / ".kanon" / "settings.yaml"))
    KanonEnv.reset()
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "source", "status"])
    assert result.exit_code == 0
    assert "mywork" not in result.output
    assert "corp" not in result.output


# ── source add validation (Step 8) ────────────────────────────────────────────


def test_source_add_rejects_kanon_project_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "kanon::project", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_rejects_kanon_self_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "kanon::self", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_rejects_gh_prefixed_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "gh::mywork", "/some/path",
    ])
    assert result.exit_code != 0


def test_source_add_allows_kanon_kanon_key(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path),
        "source", "add", "kanon::kanon", "/some/path",
    ])
    assert result.exit_code == 0, result.output
