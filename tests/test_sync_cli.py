import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import LOCAL_SCHEME, SourceReference


def make_project(root: Path, kanons: list[str], kanon_contents: dict[str, str]) -> None:
    kanon_dir = root / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {
            "kanon_version": "0.0.0",
            "kanon_sha": "abc1234",
            "integrations": ["claude"],
        },
        "kanons": kanons,
    }))
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()
    for name, content in kanon_contents.items():
        # All bare kanon names default to the kanon::kanon source, so store under kanon/kanon/
        dest = kanon_dir / "kanons" / "kanon" / "kanon" / Path(name).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def test_sync_writes_rule(tmp_path):
    make_project(tmp_path, ["git/commit-style"], {
        "git/commit-style": "Write concise commit messages.",
    })

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "kanon" / "kanon" / "git" / "commit-style.md"
    assert rule.exists()
    assert rule.read_text() == "Write concise commit messages."


def test_sync_strips_frontmatter(tmp_path):
    make_project(tmp_path, ["workflow/base"], {
        "workflow/base": "---\nkanon:\n  output: rule\n---\nFollow the workflow.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    rule = tmp_path / ".claude" / "rules" / "kanon" / "kanon" / "workflow" / "base.md"
    assert rule.read_text() == "Follow the workflow.\n"


def test_sync_no_config_exits(tmp_path):
    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])
    assert result.exit_code != 0
    assert "kanon init" in result.output


def test_sync_stance_kanons_not_rendered(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": ["git/commit-style"],
        "stances": ["focused"],
    }))
    (kanon_dir / "kanons").mkdir(parents=True)
    (kanon_dir / "kanons" / "kanon" / "kanon" / "git").mkdir(parents=True)
    (kanon_dir / "kanons" / "kanon" / "kanon" / "git" / "commit-style.md").write_text("Write good commits.")
    (kanon_dir / "kanons" / "kanon" / "kanon" / "ai").mkdir(parents=True)
    (kanon_dir / "kanons" / "kanon" / "kanon" / "ai" / "assume-and-proceed.md").write_text("Assume and proceed.")
    (kanon_dir / "stances" / "kanon" / "kanon").mkdir(parents=True)
    (kanon_dir / "stances" / "kanon" / "kanon" / "focused.yaml").write_text(yaml.dump({"kanons": ["ai/assume-and-proceed"]}))

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "rules" / "kanon" / "kanon" / "git" / "commit-style.md").exists()
    assert not (tmp_path / ".claude" / "rules" / "kanon" / "kanon" / "ai" / "assume-and-proceed.md").exists()


def test_sync_routes_command_to_skill(tmp_path):
    make_project(tmp_path, ["workflow/kanon-sketch"], {
        "workflow/kanon-sketch": "---\nkanon:\n  output: skill\n  name: kanon-sketch\n  description: Turn a vague idea into a goal\n---\nSketch the goal.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert not (tmp_path / ".claude" / "rules" / "kanon" / "kanon" / "workflow" / "kanon-sketch.md").exists()
    assert not (tmp_path / ".claude" / "commands").exists()
    skill = tmp_path / ".claude" / "skills" / "kanon-sketch" / "SKILL.md"
    assert skill.exists()
    content = skill.read_text()
    assert "Sketch the goal." in content
    assert "Turn a vague idea into a goal" in content


def test_sync_skill_name_override(tmp_path):
    make_project(tmp_path, ["workflow/kanon-sketch"], {
        "workflow/kanon-sketch": "---\nkanon:\n  output: skill\n  name: kanon-sketch\n  description: Turn a vague idea into a goal\n---\nSketch the goal.\n",
    })

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert not (tmp_path / ".claude" / "skills" / "kanon" / "kanon" / "workflow" / "kanon-sketch").exists()
    skill = tmp_path / ".claude" / "skills" / "kanon-sketch" / "SKILL.md"
    assert skill.exists()


def test_sync_skill_frontmatter(tmp_path):
    content = "\n".join([
        "---",
        "kanon:",
        "  output: skill",
        "  name: kanon-stance",
        "  description: Switch behavioral stance",
        "  skill:",
        "    args: '[stance-name]'",
        "    model_invokable: false",
        "    needs_context: false",
        "---",
        "Stance body.",
        "",
    ])
    make_project(tmp_path, ["workflow/kanon-stance"], {"workflow/kanon-stance": content})

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    skill = tmp_path / ".claude" / "skills" / "kanon-stance" / "SKILL.md"
    assert skill.exists()
    fm_text = skill.read_text()
    fm = yaml.safe_load(fm_text.split("---")[1])
    assert fm["name"] == "kanon-stance"
    assert fm["description"] == "Switch behavioral stance"
    assert fm["argument-hint"] == "[stance-name]"
    assert fm["disable-model-invocation"] is True
    assert fm["context"] == "fork"
    assert "Stance body." in fm_text


def test_sync_windsurf_command_still_flat(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {
            "kanon_version": "0.0.0",
            "kanon_sha": "abc1234",
            "integrations": ["windsurf"],
        },
        "kanons": ["workflow/kanon-sketch"],
    }))
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()
    dest = kanon_dir / "kanons" / "kanon" / "kanon" / "workflow" / "kanon-sketch.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("---\nkanon:\n  output: skill\n  name: kanon-sketch\n---\nSketch the goal.\n")

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    workflow = tmp_path / ".windsurf" / "workflows" / "kanon-sketch.md"
    assert workflow.exists()
    content = workflow.read_text()
    assert "---" in content
    assert "Sketch the goal." in content



def test_sync_devin_command_still_flat(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {
            "kanon_version": "0.0.0",
            "kanon_sha": "abc1234",
            "integrations": ["devin"],
        },
        "kanons": ["workflow/kanon-sketch"],
    }))
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()
    dest = kanon_dir / "kanons" / "kanon" / "kanon" / "workflow" / "kanon-sketch.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("---\nkanon:\n  output: skill\n  name: kanon-sketch\n---\nSketch the goal.\n")

    CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    workflow = tmp_path / ".devin" / "workflows" / "kanon-sketch.md"
    assert workflow.exists()
    content = workflow.read_text()
    assert "---" in content
    assert "Sketch the goal." in content


def test_sync_pull_external_namespace(tmp_path):
    """--pull copies external-namespace kanons from their configured source."""
    ext_kanons = tmp_path / "mywork-kanons"
    ext_kanons.mkdir()
    (ext_kanons / "kanons" / "python").mkdir(parents=True)
    (ext_kanons / "kanons" / "python" / "style.md").write_text("External style rule.")

    project = tmp_path / "project"
    project.mkdir()
    kanon_dir = project / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": ["mywork::python/style"],
        "sources": {"mywork": f"local::{ext_kanons}"},
    }))
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["--project-root", str(project), "sync", "--pull"
    ])

    assert result.exit_code == 0, result.output
    src_subpath = SourceReference(LOCAL_SCHEME, str(ext_kanons)).cache_subpath()
    assert (kanon_dir / "kanons" / src_subpath / "python" / "style.md").exists()
    assert (project / ".claude" / "rules" / src_subpath / "python" / "style.md").exists()


def test_sync_external_namespace_produces_nested_output(tmp_path):
    """External namespace 'mywork' produces rules under a path derived from the source address."""
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()

    ext_dir = tmp_path / "mywork-kanons"
    ext_dir.mkdir()
    (ext_dir / "kanons" / "python").mkdir(parents=True)
    (ext_dir / "kanons" / "python" / "style.md").write_text("Use type hints.")

    (kanon_dir / "kanon.yaml").write_text(yaml.dump({
        "meta": {"kanon_version": "0.0.0", "kanon_sha": "abc1234", "integrations": ["claude"]},
        "kanons": ["mywork::python/style"],
        "sources": {"mywork": f"local::{ext_dir}"},
    }))
    (kanon_dir / "kanons").mkdir()
    (kanon_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["--project-root", str(tmp_path), "sync"
    ])

    assert result.exit_code == 0, result.output
    src_subpath = SourceReference(LOCAL_SCHEME, str(ext_dir)).cache_subpath()
    rule = tmp_path / ".claude" / "rules" / src_subpath / "python" / "style.md"
    assert rule.exists(), result.output
    assert rule.read_text() == "Use type hints."
