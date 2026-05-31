from pathlib import Path

import yaml
from click.testing import CliRunner

from kanon.cli import cli


def make_project(root: Path, integrations: list[str] = ["claude"]) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {
            "kanon_version": "0.0.0",
            "kanon_sha": "abc1234",
            "integrations": integrations,
        },
        "kanons": [],
    }))


def test_destroy_removes_kanon_dir(tmp_path):
    make_project(tmp_path)

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "destroy", "--yes"])

    assert not (tmp_path / ".kanon").exists()


def test_destroy_removes_integration_output_dirs(tmp_path):
    make_project(tmp_path)
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    (tmp_path / ".claude" / "skills").mkdir(parents=True)

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "destroy", "--yes"])

    assert not (tmp_path / ".claude" / "rules").exists()
    assert not (tmp_path / ".claude" / "skills").exists()


def test_destroy_preserves_sibling_files(tmp_path):
    make_project(tmp_path)
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    hand_written = tmp_path / ".claude" / "CLAUDE.md"
    hand_written.write_text("# My conventions")

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "destroy", "--yes"])

    assert hand_written.exists()


def test_destroy_no_config_exits_cleanly(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "destroy", "--yes"])

    assert result.exit_code == 0
    assert "Nothing to destroy" in result.output



def test_destroy_confirms_before_removing(tmp_path):
    make_project(tmp_path)

    result = CliRunner().invoke(
        cli, ["--project-root", str(tmp_path), "destroy"], input="y\n"
    )

    assert result.exit_code == 0
    assert not (tmp_path / ".kanon").exists()


def test_destroy_abort_on_no(tmp_path):
    make_project(tmp_path)

    result = CliRunner().invoke(
        cli, ["--project-root", str(tmp_path), "destroy"], input="n\n"
    )

    assert result.exit_code != 0
    assert (tmp_path / ".kanon").exists()


def test_destroy_removes_settings_file(tmp_path):
    make_project(tmp_path)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text('{"hooks": {}}')

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "destroy", "--yes"])

    assert not settings.exists()
