import yaml
from click.testing import CliRunner

from spek.cli import cli
from spek.core.config import SpekConfig


def make_config(root, **extra):
    spek_dir = root / ".spek"
    spek_dir.mkdir(exist_ok=True)
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["git/commit-style"],
        **extra,
    }))


def test_local_module_creates_file(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "module", "my-rules"])

    assert result.exit_code == 0, result.output
    module_file = tmp_path / ".spek" / "project" / "modules" / "my-rules.md"
    assert module_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "project::my-rules" in config.modules


def test_local_module_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["--project-root", str(tmp_path), "local", "module", "my-rules"])

    result = runner.invoke(cli, ["--project-root", str(tmp_path), "local", "module", "my-rules"])

    assert result.exit_code != 0
    assert "already exists" in result.output


def test_local_module_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "module", "my-rules"])
    assert result.exit_code != 0
    assert "spek init" in result.output


def test_local_module_creates_file_in_subdirectory(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "module", "subdir/my-rules"])

    assert result.exit_code == 0, result.output
    module_file = tmp_path / ".spek" / "project" / "modules" / "subdir" / "my-rules.md"
    assert module_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "project::subdir/my-rules" in config.modules


def test_local_stance_creates_file(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    assert result.exit_code == 0, result.output
    stance_file = tmp_path / ".spek" / "project" / "stances" / "my-stance.yaml"
    assert stance_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "project::my-stance" in config.stances


def test_local_stance_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    result = runner.invoke(cli, ["--project-root", str(tmp_path), "local", "stance", "my-stance"])

    assert result.exit_code != 0
    assert "already exists" in result.output
