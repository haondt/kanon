from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from spek.core.yaml_utils import FRONTMATTER_RE, dump_yaml, parse_yaml

AI_TOOL_OUTPUT_DIRS: dict[str, dict[str, str]] = {
    "claude": {
        "rule": ".claude/rules",
        "skill": ".claude/skills",
    },
    "windsurf": {
        "rule": ".windsurf/rules",
        "skill": ".windsurf/rules",
    },
}

AI_TOOL_SETTINGS_FILES: dict[str, str] = {
    "claude": ".claude/settings.json",
}


class _SpekMeta(BaseModel):
    output: str = "rule"
    name: str | None = None
    description: str | None = None
    args: str | None = None
    integrations: dict[str, dict[str, Any]] | None = None


class ModuleFrontmatter(BaseModel):
    spek: _SpekMeta = _SpekMeta()


def parse_frontmatter(content: str) -> tuple[ModuleFrontmatter, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return ModuleFrontmatter(), content
    data: dict[str, Any] = parse_yaml(match.group(1))
    return ModuleFrontmatter.model_validate(data), content[match.end():]


def collect_hooks(content: str, ai_tool: str) -> dict[str, list[dict[str, Any]]]:
    meta, _ = parse_frontmatter(content)
    if not meta.spek.integrations:
        return {}
    tool_integrations = meta.spek.integrations.get(ai_tool, {})
    hooks = tool_integrations.get("hooks", {})
    if not hooks:
        return {}
    return {event: list(entries) for event, entries in hooks.items()}


def render_settings(hooks_by_event: dict[str, list[dict[str, Any]]], project_root: Path, ai_tool: str) -> None:
    rel = AI_TOOL_SETTINGS_FILES.get(ai_tool)
    if rel is None:
        return
    if not hooks_by_event:
        return
    settings_path = project_root / rel

    claude_hooks: dict[str, list[dict[str, Any]]] = {}
    for event, entries in hooks_by_event.items():
        groups = []
        for entry in entries:
            matcher = entry.get("matcher", "")
            command = entry.get("command", "")
            if not command:
                raise ValueError(
                    f"Hook entry for event '{event}' (matcher={matcher!r}) is missing a 'command' key"
                )
            groups.append({
                "matcher": matcher,
                "hooks": [{"type": "command", "command": command}],
            })
        claude_hooks[event] = groups

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps({"includeGitInstructions": False, "hooks": claude_hooks}, indent=2) + "\n")


def output_dir_for(project_root: Path, ai_tool: str, out_type: str) -> Path:
    tool_dirs = AI_TOOL_OUTPUT_DIRS.get(ai_tool)
    if tool_dirs is None:
        raise ValueError(f"Unknown ai_tool '{ai_tool}'. Supported: {list(AI_TOOL_OUTPUT_DIRS)}")
    rel = tool_dirs.get(out_type, tool_dirs["rule"])
    return project_root / rel


def render_module(content: str, module: str, ai_tool: str, project_root: Path) -> Path:
    meta, body = parse_frontmatter(content)
    out_type = meta.spek.output
    out_dir = output_dir_for(project_root, ai_tool, out_type)
    stem = meta.spek.name if meta.spek.name else module.replace("/", "--")

    if out_type == "skill" and ai_tool == "claude":
        skill_dir = out_dir / stem
        skill_dir.mkdir(parents=True, exist_ok=True)
        fm: dict[str, Any] = {}
        fm["name"] = stem
        if meta.spek.description:
            fm["description"] = meta.spek.description
        if meta.spek.args:
            fm["argument-hint"] = meta.spek.args
        if meta.spek.integrations:
            claude_meta = {k: v for k, v in meta.spek.integrations.get("claude", {}).items() if k != "hooks"}
            fm.update(claude_meta)
        out_path = skill_dir / "SKILL.md"
        out_path.write_text(f"---\n{dump_yaml(fm)}\n---\n{body}")
        return out_path

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (stem + ".md")
    out_path.write_text(body)
    return out_path
