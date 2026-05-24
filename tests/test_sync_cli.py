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
        # All bare module names default to the 'spek' namespace, so store under spek/
        dest = spek_dir / "modules" / "spek" / Path(name).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def test_sync_writes_rule(tmp_path):
    make_project(tmp_path, ["git/commit-style"], {
        "git/commit-style": "Write concise commit messages.",
    })

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "spek" / "git" / "commit-style.md"
    assert rule.exists()
    assert rule.read_text() == "Write concise commit messages."


def test_sync_strips_frontmatter(tmp_path):
    make_project(tmp_path, ["workflow/base"], {
        "workflow/base": "---\nspek:\n  output: rule\n---\nFollow the workflow.\n",
    })

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    rule = tmp_path / ".claude" / "rules" / "spek" / "workflow" / "base.md"
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
    (spek_dir / "modules" / "spek" / "git").mkdir(parents=True)
    (spek_dir / "modules" / "spek" / "git" / "commit-style.md").write_text("Write good commits.")
    (spek_dir / "modules" / "spek" / "ai").mkdir(parents=True)
    (spek_dir / "modules" / "spek" / "ai" / "assume-and-proceed.md").write_text("Assume and proceed.")
    (spek_dir / "stances").mkdir()
    (spek_dir / "stances" / "focused.yaml").write_text(yaml.dump({"modules": ["ai/assume-and-proceed"]}))

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "rules" / "spek" / "git" / "commit-style.md").exists()
    assert not (tmp_path / ".claude" / "rules" / "spek" / "ai" / "assume-and-proceed.md").exists()


def test_sync_routes_command_to_skill(tmp_path):
    make_project(tmp_path, ["workflow/spek-sketch"], {
        "workflow/spek-sketch": "---\nspek:\n  output: skill\n  name: spek-sketch\n  description: Turn a vague idea into a goal\n---\nSketch the goal.\n",
    })

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

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

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

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
        "  args: '[stance-name]'",
        "  integrations:",
        "    claude:",
        "      disable-model-invocation: true",
        "      context: fork",
        "---",
        "Stance body.",
        "",
    ])
    make_project(tmp_path, ["workflow/spek-stance"], {"workflow/spek-stance": content})

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

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
    dest = spek_dir / "modules" / "spek" / "workflow" / "spek-sketch.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("---\nspek:\n  output: skill\n  name: spek-sketch\n---\nSketch the goal.\n")

    CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    skill = tmp_path / ".windsurf" / "skills" / "spek-sketch" / "SKILL.md"
    assert skill.exists()
    content = skill.read_text()
    assert "---" in content
    assert "name: spek-sketch" in content
    assert "Sketch the goal." in content


def test_sync_writes_settings_for_hooks_module(tmp_path):
    content = "\n".join([
        "---",
        "spek:",
        "  integrations:",
        "    claude:",
        "      hooks:",
        "        SessionStart:",
        "          - matcher: startup",
        "            command: echo hello",
        "---",
        "Rule body.",
    ])
    make_project(tmp_path, ["workflow/base"], {"workflow/base": content})

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    settings = tmp_path / ".claude" / "settings.json"
    assert settings.exists()
    data = json.loads(settings.read_text())
    group = data["hooks"]["SessionStart"][0]
    assert group["matcher"] == "startup"
    assert group["hooks"][0]["command"] == "echo hello"


def test_sync_no_settings_when_no_hooks(tmp_path):
    make_project(tmp_path, ["workflow/base"], {"workflow/base": "Just a rule."})

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_sync_accumulates_hooks_across_modules(tmp_path):
    module_a = "\n".join([
        "---",
        "spek:",
        "  integrations:",
        "    claude:",
        "      hooks:",
        "        SessionStart:",
        "          - matcher: startup",
        "            command: echo module-a",
        "---",
        "Body A.",
    ])
    module_b = "\n".join([
        "---",
        "spek:",
        "  integrations:",
        "    claude:",
        "      hooks:",
        "        SessionStart:",
        "          - matcher: clear",
        "            command: echo module-b",
        "---",
        "Body B.",
    ])
    make_project(tmp_path, ["workflow/a", "workflow/b"], {
        "workflow/a": module_a,
        "workflow/b": module_b,
    })

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    groups = data["hooks"]["SessionStart"]
    matchers = [g["matcher"] for g in groups]
    assert "startup" in matchers
    assert "clear" in matchers


def test_sync_deletes_stale_settings_on_rehook(tmp_path):
    stale = tmp_path / ".claude" / "settings.json"
    stale.parent.mkdir(parents=True)
    stale.write_text('{"hooks": {"OldEvent": []}}')

    make_project(tmp_path, ["workflow/base"], {"workflow/base": "Just a rule."})

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert not stale.exists()


def test_sync_pull_external_namespace(tmp_path):
    """--pull copies external-namespace modules from their configured source."""
    ext_specs = tmp_path / "mywork-specs"
    ext_specs.mkdir()
    (ext_specs / "python").mkdir()
    (ext_specs / "python" / "style.md").write_text("External style rule.")

    project = tmp_path / "project"
    project.mkdir()
    spek_dir = project / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["mywork::python/style"],
        "sources": {"mywork": {"path": str(ext_specs)}},
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["sync", "--pull", "--project-root", str(project)])

    assert result.exit_code == 0, result.output
    assert (spek_dir / "modules" / "mywork" / "python" / "style.md").exists()
    assert (project / ".claude" / "rules" / "mywork" / "python" / "style.md").exists()


def test_sync_external_namespace_produces_nested_output(tmp_path):
    """External namespace 'mywork' produces rules at .claude/rules/mywork/..."""
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()

    # External source directory
    ext_dir = tmp_path / "mywork-specs"
    ext_dir.mkdir()
    (ext_dir / "python").mkdir()
    (ext_dir / "python" / "style.md").write_text("Use type hints.")

    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": ["mywork::python/style"],
        "sources": {"mywork": {"path": str(ext_dir)}},
    }))
    (spek_dir / "modules").mkdir()
    (spek_dir / "stances").mkdir()

    result = CliRunner().invoke(cli, ["sync", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    rule = tmp_path / ".claude" / "rules" / "mywork" / "python" / "style.md"
    assert rule.exists(), result.output
    assert rule.read_text() == "Use type hints."
