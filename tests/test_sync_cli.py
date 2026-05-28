import json
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
        # All bare module names default to the spek::spek source, so store under spek/spek/
        dest = spek_dir / "modules" / "spek" / "spek" / Path(name).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def test_sync_writes_rule(tmp_path):
    make_project(tmp_path, ["git/commit-style"], {
        "git/commit-style": "Write concise commit messages.",
    })

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "spek" / "spek" / "git" / "commit-style.md"
    assert rule.exists()
    assert rule.read_text() == "Write concise commit messages."


def test_sync_strips_frontmatter(tmp_path):
    make_project(tmp_path, ["workflow/base"], {
        "workflow/base": "---\nspek:\n  output: rule\n---\nFollow the workflow.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    rule = tmp_path / ".claude" / "rules" / "spek" / "spek" / "workflow" / "base.md"
    assert rule.read_text() == "Follow the workflow.\n"


def test_sync_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])
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
    (spek_dir / "modules" / "spek" / "spek" / "git").mkdir(parents=True)
    (spek_dir / "modules" / "spek" / "spek" / "git" / "commit-style.md").write_text("Write good commits.")
    (spek_dir / "modules" / "spek" / "spek" / "ai").mkdir(parents=True)
    (spek_dir / "modules" / "spek" / "spek" / "ai" / "assume-and-proceed.md").write_text("Assume and proceed.")
    (spek_dir / "stances" / "spek" / "spek").mkdir(parents=True)
    (spek_dir / "stances" / "spek" / "spek" / "focused.yaml").write_text(yaml.dump({"modules": ["ai/assume-and-proceed"]}))

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "rules" / "spek" / "spek" / "git" / "commit-style.md").exists()
    assert not (tmp_path / ".claude" / "rules" / "spek" / "spek" / "ai" / "assume-and-proceed.md").exists()


def test_sync_routes_command_to_skill(tmp_path):
    make_project(tmp_path, ["workflow/spek-sketch"], {
        "workflow/spek-sketch": "---\nspek:\n  output: skill\n  name: spek-sketch\n  description: Turn a vague idea into a goal\n---\nSketch the goal.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert not (tmp_path / ".claude" / "rules" / "spek" / "workflow" / "spek-sketch.md").exists()
    assert not (tmp_path / ".claude" / "commands").exists()
    skill = tmp_path / ".claude" / "skills" / "spek-sketch" / "SKILL.md"
    assert skill.exists()
    content = skill.read_text()
    assert "Sketch the goal." in content
    assert "Turn a vague idea into a goal" in content


def test_sync_skill_name_override(tmp_path):
    make_project(tmp_path, ["workflow/spek-sketch"], {
        "workflow/spek-sketch": "---\nspek:\n  output: skill\n  name: spek-sketch\n  description: Turn a vague idea into a goal\n---\nSketch the goal.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert not (tmp_path / ".claude" / "skills" / "spek" / "workflow" / "spek-sketch").exists()
    skill = tmp_path / ".claude" / "skills" / "spek-sketch" / "SKILL.md"
    assert skill.exists()


def test_sync_skill_frontmatter(tmp_path):
    content = "\n".join([
        "---",
        "spek:",
        "  output: skill",
        "  name: spek-stance",
        "  description: Switch behavioral stance",
        "  skill:",
        "    args: '[stance-name]'",
        "    model_invokable: false",
        "    needs_context: false",
        "---",
        "Stance body.",
        "",
    ])
    make_project(tmp_path, ["workflow/spek-stance"], {"workflow/spek-stance": content})

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    skill = tmp_path / ".claude" / "skills" / "spek-stance" / "SKILL.md"
    assert skill.exists()
    fm_text = skill.read_text()
    fm = yaml.safe_load(fm_text.split("---")[1])
    assert fm["name"] == "spek-stance"
    assert fm["description"] == "Switch behavioral stance"
    assert fm["argument-hint"] == "[stance-name]"
    assert fm["disable-model-invocation"] is True
    assert fm["context"] == "fork"
    assert "Stance body." in fm_text


def test_sync_windsurf_command_still_flat(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {
            "spek_version": "0.0.0",
            "spek_sha": "abc1234",
            "integrations": ["windsurf"],
        },
        "modules": ["workflow/spek-sketch"],
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()
    dest = spek_dir / "modules" / "spek" / "spek" / "workflow" / "spek-sketch.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("---\nspek:\n  output: skill\n  name: spek-sketch\n---\nSketch the goal.\n")

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    workflow = tmp_path / ".windsurf" / "workflows" / "spek-sketch.md"
    assert workflow.exists()
    content = workflow.read_text()
    assert "---" in content
    assert "Sketch the goal." in content



def test_sync_pull_external_namespace(tmp_path):
    """--pull copies external-namespace modules from their configured source."""
    ext_specs = tmp_path / "mywork-specs"
    ext_specs.mkdir()
    (ext_specs / "specs" / "python").mkdir(parents=True)
    (ext_specs / "specs" / "python" / "style.md").write_text("External style rule.")

    project = tmp_path / "project"
    project.mkdir()
    spek_dir = project / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["mywork::python/style"],
        "sources": {"mywork": f"local::{ext_specs}"},
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["--project-root", str(project), "sync", "--pull"
    ])

    assert result.exit_code == 0, result.output
    assert (spek_dir / "modules" / "alias" / "mywork" / "python" / "style.md").exists()
    assert (project / ".claude" / "rules" / "alias" / "mywork" / "python" / "style.md").exists()


def test_sync_external_namespace_produces_nested_output(tmp_path):
    """External namespace 'mywork' produces rules at .claude/rules/mywork/..."""
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()

    # External source directory
    ext_dir = tmp_path / "mywork-specs"
    ext_dir.mkdir()
    (ext_dir / "specs" / "python").mkdir(parents=True)
    (ext_dir / "specs" / "python" / "style.md").write_text("Use type hints.")

    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["mywork::python/style"],
        "sources": {"mywork": f"local::{ext_dir}"},
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "alias" / "mywork" / "python" / "style.md"
    assert rule.exists(), result.output
    assert rule.read_text() == "Use type hints."
