from __future__ import annotations

import json

import yaml
from click.testing import CliRunner
from pathlib import Path

from spek.cli import cli
from spek.core.config import SpekConfig


def make_config(root: Path, modules: list[str] | None = None, **extra) -> None:
    spek_dir = root / ".spek"
    spek_dir.mkdir(exist_ok=True)
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": modules or ["git/commit-base"],
        **extra,
    }))


# ── module list ───────────────────────────────────────────────────────────────


def test_module_list_json_returns_list(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "list", "--json", ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0


def test_module_list_json_entry_shape(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "list", "--json", ])
    entry = json.loads(result.output)[0]
    assert "name" in entry
    assert "description" in entry
    assert "active" in entry
    assert "source" in entry


def test_module_list_json_marks_active_correctly(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "list", "--json", ])
    by_name = {e["name"]: e for e in json.loads(result.output)}
    assert by_name["git/commit-base"]["active"] is True
    assert by_name["python/style"]["active"] is False


def test_module_list_default_output_shows_checkmark(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "list", ])
    assert result.exit_code == 0, result.output
    assert "[✓]" in result.output
    assert "git/commit-base" in result.output


# ── module set ────────────────────────────────────────────────────────────────


def test_module_set_saves_modules(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "set", "python/style", "git/commit-base"
    ])
    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert set(config.modules) == {"python/style", "git/commit-base"}


def test_module_set_replaces_existing(tmp_path):
    make_config(tmp_path, modules=["git/commit-base", "python/style"])
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "set", "code/hygiene"
    ])
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert config.modules == ["code/hygiene"]


def test_module_set_rejects_unknown_module(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "set", "not/a/real/module"
    ])
    assert result.exit_code != 0
    assert "not/a/real/module" in result.output


def test_module_set_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "set", "git/commit-base"
    ])
    assert result.exit_code != 0
    assert "spek init" in result.output


def test_module_set_preserves_stances_and_meta(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "1.2.3", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["git/commit-base"],
        "stances": ["autonomous", "collaborative"],
    }))
    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "set", "python/style"
    ])
    config = SpekConfig.load(spek_dir / "spek.yaml")
    assert config.modules == ["python/style"]
    assert config.stances == ["autonomous", "collaborative"]
    assert config.meta.spek_version == "1.2.3"


# ── module group ──────────────────────────────────────────────────────────────


def test_module_bare_shows_subcommands(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module"])
    assert "edit" in result.output
    assert "list" in result.output
    assert "set" in result.output
    assert "add" in result.output
    assert "remove" in result.output
    assert "search" in result.output


# ── module add ────────────────────────────────────────────────────────────────


def test_module_add_appends_to_existing(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, [
        "--project-root", str(tmp_path), "module", "add", "python/style"
    ])
    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "git/commit-base" in config.modules
    assert "python/style" in config.modules


def test_module_add_rejects_unknown(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "add", "not/real"
    ])
    assert result.exit_code != 0
    assert "not/real" in result.output


def test_module_add_already_active_reports_message(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "add", "git/commit-base"
    ])
    assert result.exit_code == 0
    assert "already active" in result.output


def test_module_add_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "add", "git/commit-base"
    ])
    assert result.exit_code != 0
    assert "spek init" in result.output


# ── module remove ─────────────────────────────────────────────────────────────


def test_module_remove_deletes_module(tmp_path):
    make_config(tmp_path, modules=["git/commit-base", "python/style"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "remove", "python/style"
    ])
    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "python/style" not in config.modules
    assert "git/commit-base" in config.modules


def test_module_remove_inactive_is_noop(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "remove", "python/style"
    ])
    assert result.exit_code == 0
    assert "inactive" in result.output


def test_module_remove_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "remove", "git/commit-base"
    ])
    assert result.exit_code != 0
    assert "spek init" in result.output


# ── module search ─────────────────────────────────────────────────────────────


def test_module_search_finds_matching(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "search", "git"
    ])
    assert result.exit_code == 0, result.output
    assert "git" in result.output


def test_module_search_json_returns_list(tmp_path):
    import json
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "search", "git", "--json"
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


def test_module_search_marks_active(tmp_path):
    import json
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "search", "commit-base", "--json"
    ])
    data = json.loads(result.output)
    assert data[0]["active"] is True


def test_module_search_requires_all_terms(tmp_path):
    import json
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "module", "search", "git", "xxxxxxxxnotreal", "--json"
    ])
    data = json.loads(result.output)
    assert data == []
