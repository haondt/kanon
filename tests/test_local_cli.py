import yaml
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import KanonConfig


def make_config(root, **extra):
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir(exist_ok=True)
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": ["git/commit-style"],
        **extra,
    }))


def test_local_kanon_creates_file(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "kanon", "my-rules"])

    assert result.exit_code == 0, result.output
    kanon_file = tmp_path / ".kanon" / "project" / "kanons" / "my-rules.md"
    assert kanon_file.exists()
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "project::my-rules" in config.kanons


def test_local_kanon_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["--project-root", str(tmp_path), "local", "kanon", "my-rules"])

    result = runner.invoke(cli, ["--project-root", str(tmp_path), "local", "kanon", "my-rules"])

    assert result.exit_code != 0
    assert "already exists" in result.output


def test_local_kanon_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "kanon", "my-rules"])
    assert result.exit_code != 0
    assert "kanon init" in result.output


def test_local_kanon_creates_file_in_subdirectory(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "kanon", "subdir/my-rules"])

    assert result.exit_code == 0, result.output
    kanon_file = tmp_path / ".kanon" / "project" / "kanons" / "subdir" / "my-rules.md"
    assert kanon_file.exists()
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "project::subdir/my-rules" in config.kanons


def test_local_stance_creates_file(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    assert result.exit_code == 0, result.output
    stance_file = tmp_path / ".kanon" / "project" / "stances" / "my-stance.yaml"
    assert stance_file.exists()
    config = KanonConfig.load(tmp_path / ".kanon" / "kanon.yaml")
    assert "project::my-stance" in config.stances


def test_local_stance_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    result = runner.invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    assert result.exit_code != 0
    assert "already exists" in result.output
