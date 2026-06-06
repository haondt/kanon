from pathlib import Path
import json
import yaml
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import KanonConfig


def make_config(root, profile=None):
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    meta = {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]}
    if profile:
        meta["profile"] = profile
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": meta,
        "kanons": ["git/commit-style"],
    }))


def test_profile_apply_updates_config(tmp_path: Path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "base/base"])

    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert config.meta.profile == "base/base"
    assert "workflow/base" in config.kanons
    assert "git/commit-style" in config.kanons


def test_profile_apply_additive_preserves_existing(tmp_path: Path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "base/base"])

    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "git/commit-style" in config.kanons
    assert "workflow/base" in config.kanons


def test_profile_apply_replace_flag_replaces(tmp_path: Path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "--replace", "base/base"])

    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "git/commit-style" not in config.kanons
    assert "workflow/base" in config.kanons


def test_profile_apply_uses_recorded_profile(tmp_path: Path):
    make_config(tmp_path, profile="base/base")

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply"])

    assert result.exit_code == 0, result.output
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert config.meta.profile == "base/base"


def test_profile_apply_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "base/git"])
    assert result.exit_code != 0
    assert "kanon init" in result.output


def test_profile_apply_no_name_no_recorded_profile_exits(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply"])

    assert result.exit_code != 0
    assert "No profile" in result.output


def test_profile_list_shows_profiles():
    result = CliRunner().invoke(cli, ["profile", "list"])
    assert result.exit_code == 0, result.output
    assert "base/base" in result.output
    assert "python/cli" in result.output


def test_profile_search_finds_by_name():
    result = CliRunner().invoke(cli, ["profile", "search", "base"])
    assert result.exit_code == 0, result.output
    assert "base/base" in result.output


def test_profile_search_no_results():
    result = CliRunner().invoke(cli, ["profile", "search", "xyzzy_no_such_profile_12345"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == ""


def test_profile_search_json():
    result = CliRunner().invoke(cli, ["profile", "search", "--json", "base"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("name" in item and "description" in item for item in data)
