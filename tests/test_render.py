from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from spek.core.render import collect_hooks, collect_preapproved_tools, render_module, render_settings


def _hooks_content(*entries: dict) -> str:
    lines = ["---", "spek:", "  integrations:", "    claude:", "      hooks:", "        SessionStart:"]
    for e in entries:
        matcher = e.get("matcher", "")
        lines.append(f"          - matcher: {matcher}")
        if "command" in e:
            lines.append(f"            command: {e['command']}")
    lines += ["---", "Body."]
    return "\n".join(lines)


def test_collect_hooks_returns_empty_without_integrations():
    assert collect_hooks("Just some text.", "claude") == {}


def test_collect_hooks_returns_empty_without_hooks_key():
    content = "---\nspek:\n  integrations:\n    claude:\n      context: fork\n---\nBody."
    assert collect_hooks(content, "claude") == {}


def test_collect_hooks_returns_hooks():
    content = _hooks_content({"matcher": "startup", "command": "echo hello"})
    result = collect_hooks(content, "claude")
    assert result == {"SessionStart": [{"matcher": "startup", "command": "echo hello"}]}


def test_collect_hooks_ignores_other_tool():
    content = _hooks_content({"matcher": "startup", "command": "echo hello"})
    assert collect_hooks(content, "windsurf") == {}


def test_collect_hooks_skips_skill_output():
    content = "---\nspek:\n  output: skill\n  integrations:\n    claude:\n      hooks:\n        SessionStart:\n          - matcher: startup\n            command: echo hello\n---\nBody."
    assert collect_hooks(content, "claude") == {}


def test_collect_preapproved_tools_returns_empty_without_field():
    assert collect_preapproved_tools("Just some text.") == []


def test_collect_preapproved_tools_returns_tools():
    content = "---\nspek:\n  preapproved_tools:\n    - Bash(spek ref *)\n    - Skill(my-skill)\n---\nBody."
    assert collect_preapproved_tools(content) == ["Bash(spek ref *)", "Skill(my-skill)"]


def test_collect_preapproved_tools_skips_skill_output():
    content = "---\nspek:\n  output: skill\n  preapproved_tools:\n    - Bash(spek ref *)\n---\nBody."
    assert collect_preapproved_tools(content) == []


def test_render_settings_writes_permissions(tmp_path):
    render_settings({}, tmp_path, "claude", ["Bash(spek ref *)", "Skill(my-skill)"])
    settings = tmp_path / ".claude" / "settings.json"
    assert settings.exists()
    data = json.loads(settings.read_text())
    assert data["permissions"] == {"allow": ["Bash(spek ref *)", "Skill(my-skill)"]}
    assert data["includeGitInstructions"] == False


def test_render_settings_no_hooks_no_tools_skips_file(tmp_path):
    render_settings({}, tmp_path, "claude", [])
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_render_settings_writes_json(tmp_path):
    hooks = {"SessionStart": [{"matcher": "startup", "command": "echo hello"}]}
    render_settings(hooks, tmp_path, "claude")
    settings = tmp_path / ".claude" / "settings.json"
    assert settings.exists()
    data = json.loads(settings.read_text())
    assert data == {
        "hooks": {
            "SessionStart": [
                {"matcher": "startup", "hooks": [{"type": "command", "command": "echo hello"}]}
            ]
        },
        "includeGitInstructions": False,
    }


def test_render_settings_no_hooks_skips_file(tmp_path):
    render_settings({}, tmp_path, "claude")
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_render_settings_unknown_tool_skips(tmp_path):
    hooks = {"SessionStart": [{"matcher": "", "command": "echo hi"}]}
    render_settings(hooks, tmp_path, "windsurf")
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_render_settings_missing_command_raises(tmp_path):
    hooks = {"SessionStart": [{"matcher": "startup"}]}
    with pytest.raises(ValueError, match="command"):
        render_settings(hooks, tmp_path, "claude")


def test_render_settings_empty_command_raises(tmp_path):
    hooks = {"SessionStart": [{"matcher": "startup", "command": ""}]}
    with pytest.raises(ValueError, match="command"):
        render_settings(hooks, tmp_path, "claude")


def _fork_skill_content(ai_tool: str = "claude") -> str:
    return dedent(f"""\
        ---
        spek:
          output: skill
          name: my-skill
          description: A test skill
          integrations:
            {ai_tool}:
              disable-model-invocation: true
              context: fork
        ---
        Do the thing.
        """)


def test_render_module_fork_skill_appends_preload_command(tmp_path):
    content = _fork_skill_content("claude")
    render_module(content, "workflow/my-skill", "claude", tmp_path)
    skill_md = (tmp_path / ".claude/skills/my-skill/SKILL.md").read_text()
    assert "## Project structure\n\n!`test -f .spek/STRUCTURE.md && cat .spek/STRUCTURE.md`" in skill_md
    assert "Bash(test .spek/STRUCTURE.md)" in skill_md
    assert "Bash(cat .spek/STRUCTURE.md)" in skill_md


def test_render_module_windsurf_fork_skill_no_preload(tmp_path):
    content = _fork_skill_content("windsurf")
    render_module(content, "workflow/my-skill", "windsurf", tmp_path)
    skill_md = (tmp_path / ".windsurf/skills/my-skill.md").read_text()
    assert "!`test -f" not in skill_md


def test_render_module_skill_merges_preapproved_and_integration_allowed_tools(tmp_path):
    content = dedent("""\
        ---
        spek:
          output: skill
          name: merge-test
          description: Test merging allowed-tools
          preapproved_tools:
            - Bash(spek ref *)
          integrations:
            claude:
              allowed-tools:
                - Skill(other-skill)
        ---
        Body.
        """)
    render_module(content, "test/merge-test", "claude", tmp_path)
    skill_md = (tmp_path / ".claude/skills/merge-test/SKILL.md").read_text()
    assert "Bash(spek ref *)" in skill_md
    assert "Skill(other-skill)" in skill_md
