from __future__ import annotations

import yaml
from click.testing import CliRunner
from pathlib import Path

from spek.cli import cli


def make_config(root: Path, modules: list[str] | None = None, **extra) -> None:
    spek_dir = root / ".spek"
    spek_dir.mkdir(exist_ok=True)
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": modules or [],
        **extra,
    }))


def test_check_passes_with_valid_modules(tmp_path):
    make_config(tmp_path, modules=["git/commit-base"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code == 0, result.output
    assert "All checks passed." in result.output


def test_check_fails_with_unknown_module(tmp_path):
    make_config(tmp_path, modules=["not/a/real/module"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code != 0
    assert "not/a/real/module" in result.output
    assert "error" in result.output


def test_check_fails_with_missing_local_source(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    make_config(tmp_path, sources={"mywork": f"local::{tmp_path / 'nonexistent'}"})
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code != 0
    assert "error" in result.output


def test_check_reports_remote_source_as_info(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    make_config(tmp_path, sources={"upstream": "gh::org/repo"})
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code == 0
    assert "info" in result.output
    assert "not yet fetched" in result.output


def test_check_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code != 0
    assert "spek init" in result.output
