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
    result = CliRunner().invoke(cli, ["module", "list", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0


def test_module_list_json_entry_shape(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, ["module", "list", "--json", "--project-root", str(tmp_path)])
    entry = json.loads(result.output)[0]
    assert "name" in entry
    assert "description" in entry
    assert "active" in entry


def test_module_list_json_marks_active_correctly(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["module", "list", "--json", "--project-root", str(tmp_path)])
    by_name = {e["name"]: e for e in json.loads(result.output)}
    assert by_name["git/commit-base"]["active"] is True
    assert by_name["python/style"]["active"] is False


def test_module_list_default_output_shows_checkmark(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["module", "list", "--project-root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "[✓]" in result.output
    assert "git/commit-base" in result.output


# ── module set ────────────────────────────────────────────────────────────────


def test_module_set_saves_modules(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, [
        "module", "set", "python/style", "git/commit-base",
        "--project-root", str(tmp_path),
    ])
    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert config.modules == ["python/style", "git/commit-base"]


def test_module_set_replaces_existing(tmp_path):
    make_config(tmp_path, modules=["git/commit-base", "python/style"])
    CliRunner().invoke(cli, [
        "module", "set", "code/hygiene",
        "--project-root", str(tmp_path),
    ])
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert config.modules == ["code/hygiene"]


def test_module_set_rejects_unknown_module(tmp_path):
    make_config(tmp_path)
    result = CliRunner().invoke(cli, [
        "module", "set", "not/a/real/module",
        "--project-root", str(tmp_path),
    ])
    assert result.exit_code != 0
    assert "not/a/real/module" in result.output


def test_module_set_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, [
        "module", "set", "git/commit-base",
        "--project-root", str(tmp_path),
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
    CliRunner().invoke(cli, [
        "module", "set", "python/style",
        "--project-root", str(tmp_path),
    ])
    config = SpekConfig.load(spek_dir / "spek.yaml")
    assert config.modules == ["python/style"]
    assert config.stances == ["autonomous", "collaborative"]
    assert config.meta.spek_version == "1.2.3"


# ── module group ──────────────────────────────────────────────────────────────


def test_module_bare_shows_subcommands(tmp_path):
    result = CliRunner().invoke(cli, ["module"])
    assert "edit" in result.output
    assert "list" in result.output
    assert "set" in result.output
