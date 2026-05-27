import yaml
from click.testing import CliRunner

from spek.cli import cli
from spek.core.config import SpekConfig


def make_config(root, profile=None):
    spek_dir = root / ".spek"
    spek_dir.mkdir(exist_ok=True)
    meta = {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]}
    if profile:
        meta["profile"] = profile
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": meta,
        "modules": ["git/commit-style"],
    }))


def test_profile_apply_updates_config(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "base/git"])

    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert config.meta.profile == "base/git"
    assert "git/commit-base" in config.modules


def test_profile_apply_uses_recorded_profile(tmp_path):
    make_config(tmp_path, profile="base/git")

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply"])

    assert result.exit_code == 0, result.output
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert config.meta.profile == "base/git"


def test_profile_apply_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "profile", "apply", "base/git"])
    assert result.exit_code != 0
    assert "spek init" in result.output


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
