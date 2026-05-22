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

    result = CliRunner().invoke(cli, ["local", "module", "my-rules", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    module_file = tmp_path / ".spek" / "local" / "modules" / "my-rules.md"
    assert module_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "my-rules" in config.local_modules


def test_local_module_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["local", "module", "my-rules", "--project-root", str(tmp_path)])

    result = runner.invoke(cli, ["local", "module", "my-rules", "--project-root", str(tmp_path)])

    assert result.exit_code != 0
    assert "already exists" in result.output


def test_local_module_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["local", "module", "my-rules", "--project-root", str(tmp_path)])
    assert result.exit_code != 0
    assert "spek init" in result.output


def test_local_module_creates_file_in_subdirectory(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["local", "module", "subdir/my-rules", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    module_file = tmp_path / ".spek" / "local" / "modules" / "subdir" / "my-rules.md"
    assert module_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert "subdir/my-rules" in config.local_modules


def test_local_stance_creates_file(tmp_path):
    make_config(tmp_path)

    result = CliRunner().invoke(cli, ["local", "stance", "my-stance", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    stance_file = tmp_path / ".spek" / "local" / "stances" / "my-stance.yaml"
    assert stance_file.exists()
    config = SpekConfig.load(tmp_path / ".spek" / "spek.yaml")
    assert ".spek/local/stances/my-stance.yaml" in config.local_stances


def test_local_stance_duplicate_exits(tmp_path):
    make_config(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["local", "stance", "my-stance", "--project-root", str(tmp_path)])

    result = runner.invoke(cli, ["local", "stance", "my-stance", "--project-root", str(tmp_path)])

    assert result.exit_code != 0
    assert "already exists" in result.output
