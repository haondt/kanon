from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from spek.core.render import collect_hooks, render_settings


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
