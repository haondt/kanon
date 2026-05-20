from pathlib import Path

import yaml
from click.testing import CliRunner

from spek.cli import cli


def make_project(root: Path, modules: list[str], module_contents: dict[str, str]) -> None:
    spek_dir = root / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {
            "spek_version": "0.0.0",
            "spek_sha": "abc1234",
            "integrations": ["claude"],
        },
        "modules": modules,
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()
    for name, content in module_contents.items():
        dest = spek_dir / "modules" / Path(name).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def test_sync_writes_rule(tmp_path):
    make_project(tmp_path, ["git/commit-style"], {
        "git/commit-style": "Write concise commit messages.",
    })

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "git--commit-style.md"
    assert rule.exists()
    assert rule.read_text() == "Write concise commit messages."


def test_sync_strips_frontmatter(tmp_path):
    make_project(tmp_path, ["workflow/base"], {
        "workflow/base": "---\nspek:\n  output: rule\n---\nFollow the workflow.\n",
    })

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    rule = tmp_path / ".claude" / "rules" / "workflow--base.md"
    assert rule.read_text() == "Follow the workflow.\n"


def test_sync_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])
    assert result.exit_code != 0
    assert "spek init" in result.output


def test_sync_stance_modules_not_rendered(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["git/commit-style"],
        "stances": ["focused"],
    }))
    (spek_dir / "modules").mkdir(parents=True)
    (spek_dir / "modules" / "git").mkdir()
    (spek_dir / "modules" / "git" / "commit-style.md").write_text("Write good commits.")
    (spek_dir / "modules" / "ai").mkdir()
    (spek_dir / "modules" / "ai" / "assume-and-proceed.md").write_text("Assume and proceed.")
    (spek_dir / "stances").mkdir()
    (spek_dir / "stances" / "focused.yaml").write_text(yaml.dump({"modules": ["ai/assume-and-proceed"]}))

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "rules" / "git--commit-style.md").exists()
    assert not (tmp_path / ".claude" / "rules" / "ai--assume-and-proceed.md").exists()


def test_sync_routes_command_output(tmp_path):
    make_project(tmp_path, ["workflow/spek-define"], {
        "workflow/spek-define": "---\nspek:\n  output: command\n---\nDefine the session goal.\n",
    })

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert not (tmp_path / ".claude" / "rules" / "workflow--spek-define.md").exists()
    cmd = tmp_path / ".claude" / "commands" / "workflow--spek-define.md"
    assert cmd.exists()
    assert cmd.read_text() == "Define the session goal.\n"


def test_sync_command_name_override(tmp_path):
    make_project(tmp_path, ["workflow/spek-define"], {
        "workflow/spek-define": "---\nspek:\n  output: command\n  name: spek-define\n---\nDefine the session goal.\n",
    })

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert not (tmp_path / ".claude" / "commands" / "workflow--spek-define.md").exists()
    cmd = tmp_path / ".claude" / "commands" / "spek-define.md"
    assert cmd.exists()
    assert cmd.read_text() == "Define the session goal.\n"
