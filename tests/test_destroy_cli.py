from pathlib import Path

import yaml
from click.testing import CliRunner

from spek.cli import cli


def make_project(root: Path, integrations: list[str] = ["claude"]) -> None:
    spek_dir = root / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {
            "spek_version": "0.0.0",
            "spek_sha": "abc1234",
            "integrations": integrations,
        },
        "modules": [],
    }))


def test_destroy_removes_spek_dir(tmp_path):
    make_project(tmp_path)

    CliRunner().invoke(cli, ["destroy", "--project-root", str(tmp_path), "--yes"])

    assert not (tmp_path / ".spek").exists()


def test_destroy_removes_integration_output_dirs(tmp_path):
    make_project(tmp_path)
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    (tmp_path / ".claude" / "commands").mkdir(parents=True)

    CliRunner().invoke(cli, ["destroy", "--project-root", str(tmp_path), "--yes"])

    assert not (tmp_path / ".claude" / "rules").exists()
    assert not (tmp_path / ".claude" / "commands").exists()


def test_destroy_preserves_sibling_files(tmp_path):
    make_project(tmp_path)
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    hand_written = tmp_path / ".claude" / "CLAUDE.md"
    hand_written.write_text("# My conventions")

    CliRunner().invoke(cli, ["destroy", "--project-root", str(tmp_path), "--yes"])

    assert hand_written.exists()


def test_destroy_no_config_exits_cleanly(tmp_path):
    result = CliRunner().invoke(cli, ["destroy", "--project-root", str(tmp_path), "--yes"])

    assert result.exit_code == 0
    assert "Nothing to destroy" in result.output



def test_destroy_confirms_before_removing(tmp_path):
    make_project(tmp_path)

    result = CliRunner().invoke(
        cli, ["destroy", "--project-root", str(tmp_path)], input="y\n"
    )

    assert result.exit_code == 0
    assert not (tmp_path / ".spek").exists()


def test_destroy_abort_on_no(tmp_path):
    make_project(tmp_path)

    result = CliRunner().invoke(
        cli, ["destroy", "--project-root", str(tmp_path)], input="n\n"
    )

    assert result.exit_code != 0
    assert (tmp_path / ".spek").exists()
