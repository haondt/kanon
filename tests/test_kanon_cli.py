from __future__ import annotations

import json

import yaml
from click.testing import CliRunner
from pathlib import Path

from kanon.cli import cli
from kanon.core.config import KanonConfig


def make_config(root: Path, kanons: list[str] | None = None, **extra) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": kanons or ["git/commit-base"],
        **extra,
    }))


# ── kanon list ────────────────────────────────────────────────────────────────


def test_kanon_list_json_returns_list(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "list", "--json", ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0


def test_kanon_list_json_entry_shape(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "list", "--json", ])
    entry = json.loads(result.output)[0]
    assert "name" in entry
    assert "description" in entry
    assert "active" in entry
    assert "source" in entry


def test_kanon_list_json_marks_active_correctly(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "list", "--json", ])
    by_name = {e["name"]: e for e in json.loads(result.output)}
    assert by_name["tools/kanon/kanons"]["active"] is True
    assert by_name["tools/kanon/session"]["active"] is False


def test_kanon_list_default_output_shows_checkmark(tmp_path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "list", ])
    assert result.exit_code == 0, result.output
    assert "[✓]" in result.output
    assert "tools/kanon/kanons" in result.output


# ── kanon set ─────────────────────────────────────────────────────────────────


def test_kanon_set_saves_kanons(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "tools/kanon/session", "tools/kanon/kanons"
    ])
    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert set(config.kanons) == {"tools/kanon/session", "tools/kanon/kanons"}


def test_kanon_set_replaces_existing(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons", "tools/kanon/session"])
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "systems/base"
    ])
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert config.kanons == ["systems/base"]


def test_kanon_set_rejects_unknown_kanon(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "not/a/real/kanon"
    ])
    assert result.exit_code != 0
    assert "not/a/real/kanon" in result.output


def test_kanon_set_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "git/commit-base"
    ])
    assert result.exit_code != 0
    assert "kanon init" in result.output


def test_kanon_set_deduplicates_repeated_kanons(tmp_path: Path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "tools/kanon/kanons", "tools/kanon/kanons", "tools/kanon/session"
    ])
    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert config.kanons.count("tools/kanon/kanons") == 1
    assert set(config.kanons) == {"tools/kanon/kanons", "tools/kanon/session"}


def test_kanon_set_preserves_stances_and_meta(tmp_path: Path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "1.2.3", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": ["tools/kanon/kanons"],
        "stances": ["autonomous", "collaborative"],
    }))
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "set", "tools/kanon/session"
    ])
    config = KanonConfig.load(kanon_dir / "kanon.yaml")
    assert config.kanons == ["tools/kanon/session"]
    assert config.stances == ["autonomous", "collaborative"]
    assert config.meta.kanon_version == "1.2.3"


# ── top-level kanon commands ──────────────────────────────────────────────────


def test_top_level_shows_kanon_commands(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "--help"])
    assert "edit" in result.output
    assert "list" in result.output
    assert "set" in result.output
    assert "add" in result.output
    assert "remove" in result.output
    assert "search" in result.output


# ── kanon add ─────────────────────────────────────────────────────────────────


def test_kanon_add_appends_to_existing(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path), "add", "tools/kanon/session"
    ])
    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "tools/kanon/kanons" in config.kanons
    assert "tools/kanon/session" in config.kanons


def test_kanon_add_rejects_unknown(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "add", "not/real"
    ])
    assert result.exit_code != 0
    assert "not/real" in result.output


def test_kanon_add_already_active_reports_message(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "add", "tools/kanon/kanons"
    ])
    assert result.exit_code == 0
    assert "already active" in result.output


def test_kanon_add_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "add", "tools/kanon/kanons"
    ])
    assert result.exit_code != 0
    assert "kanon init" in result.output


# ── kanon remove ──────────────────────────────────────────────────────────────


def test_kanon_remove_deletes_kanon(tmp_path):
    make_config(tmp_path, kanons=["git/commit-base", "python/style"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "remove", "python/style"
    ])
    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "python/style" not in config.kanons
    assert "git/commit-base" in config.kanons


def test_kanon_remove_inactive_is_noop(tmp_path):
    make_config(tmp_path, kanons=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "remove", "python/style"
    ])
    assert result.exit_code == 0
    assert "inactive" in result.output


def test_kanon_remove_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "remove", "git/commit-base"
    ])
    assert result.exit_code != 0
    assert "kanon init" in result.output


# ── kanon search ──────────────────────────────────────────────────────────────


def test_kanon_search_finds_matching(tmp_path: Path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "search", "kanon"
    ])
    assert result.exit_code == 0, result.output
    assert "kanon" in result.output


def test_kanon_search_json_returns_list(tmp_path: Path):
    import json
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "search", "kanon", "--json"
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0
    entry = data[0]
    assert "name" in entry
    assert "description" in entry
    assert "active" in entry
    assert "source" in entry


def test_kanon_search_marks_active(tmp_path: Path):
    import json
    make_config(tmp_path, kanons=["systems/base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "search", "base", "--json"
    ])
    data = json.loads(result.output)
    assert data[0]["active"] is True


def test_kanon_search_requires_all_terms(tmp_path):
    import json
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "search", "git", "xxxxxxxxnotreal", "--json"
    ])
    data = json.loads(result.output)
    assert data == []
