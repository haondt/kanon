from __future__ import annotations

import yaml
from click.testing import CliRunner
from pathlib import Path

from kanon.cli import cli


def make_config(root: Path, kanons: list[str] | None = None, **extra) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": kanons or [],
        **extra,
    }))


def test_check_passes_with_valid_kanons(tmp_path: Path):
    make_config(tmp_path, kanons=["tools/kanon/kanons"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code == 0, result.output
    assert "All checks passed." in result.output


def test_check_fails_with_unknown_kanon(tmp_path):
    make_config(tmp_path, kanons=["not/a/real/kanon"])
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "check"])
    assert result.exit_code != 0
    assert "not/a/real/kanon" in result.output
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
    assert "kanon init" in result.output
