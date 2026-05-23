from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import jinja2
from pydantic import BaseModel

from spek.core.utils import deep_merge
from spek.core.yaml_utils import FRONTMATTER_RE, dump_yaml, parse_yaml

AI_TOOL_OUTPUT_DIRS: dict[str, dict[str, str]] = {
    "claude": {
        "rule": ".claude/rules",
        "skill": ".claude/skills",
    },
    "windsurf": {
        "rule": ".windsurf/rules",
        "skill": ".windsurf/skills",
    },
}

AI_TOOL_SETTINGS_FILES: dict[str, str] = {
    "claude": ".claude/settings.json",
}

AI_TOOL_ADDITIONAL_SETTINGS: dict[str, dict[str, Any]] = {
    "claude": {
        "includeGitInstructions": False,
    }
}


class _SpekMeta(BaseModel):
    output: Literal["rule", "skill"] = "rule"
    name: str | None = None
    description: str | None = None
    args: str | None = None
    integrations: dict[str, dict[str, Any]] | None = None
    preapproved_tools: list[str] = []
    template: Literal["jinja"] | None = None


class ModuleFrontmatter(BaseModel):
    spek: _SpekMeta = _SpekMeta()


def _apply_jinja(body: str, context: dict[str, Any]) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, keep_trailing_newline=True)
    return env.from_string(body).render(**context)


def parse_frontmatter(content: str) -> tuple[ModuleFrontmatter, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return ModuleFrontmatter(), content
    data: dict[str, Any] = parse_yaml(match.group(1))
    return ModuleFrontmatter.model_validate(data), content[match.end():]


def collect_preapproved_tools(content: str) -> list[str]:
    meta, _ = parse_frontmatter(content)
    if meta.spek.output == "skill":
        return []
    return list(meta.spek.preapproved_tools)


def collect_hooks(content: str, ai_tool: str) -> dict[str, list[dict[str, Any]]]:
    meta, _ = parse_frontmatter(content)
    if meta.spek.output == "skill":
        return {}
    if not meta.spek.integrations:
        return {}
    tool_integrations = meta.spek.integrations.get(ai_tool, {})
    hooks = tool_integrations.get("hooks", {})
    if not hooks:
        return {}
    return {event: list(entries) for event, entries in hooks.items()}


def render_settings(
    hooks_by_event: dict[str, list[dict[str, Any]]],
    project_root: Path,
    ai_tool: str,
    preapproved_tools: list[str] | None = None,
) -> None:
    rel = AI_TOOL_SETTINGS_FILES.get(ai_tool)
    if rel is None:
        return
    preapproved_tools = preapproved_tools or []
    if not hooks_by_event and not preapproved_tools:
        return
    settings_path = project_root / rel

    hooks: dict[str, list[dict[str, Any]]] = {}
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
        hooks[event] = groups

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_object: dict[str, Any] = {}
    if preapproved_tools:
        settings_object["permissions"] = {"allow": preapproved_tools}
    if hooks:
        settings_object["hooks"] = hooks
    additional_settings = AI_TOOL_ADDITIONAL_SETTINGS.get(ai_tool)
    if additional_settings:
        settings_object = deep_merge(settings_object, additional_settings)
    settings_path.write_text(json.dumps(settings_object, indent=2) + "\n")


def output_dir_for(project_root: Path, ai_tool: str, out_type: str) -> Path:
    tool_dirs = AI_TOOL_OUTPUT_DIRS.get(ai_tool)
    if tool_dirs is None:
        raise ValueError(f"Unknown ai_tool '{ai_tool}'. Supported: {list(AI_TOOL_OUTPUT_DIRS)}")
    rel = tool_dirs.get(out_type, tool_dirs["rule"])
    return project_root / rel


def render_module(
    content: str,
    module: str,
    ai_tool: str,
    project_root: Path,
    modules: list[str] | None = None,
    integrations: list[str] | None = None,
) -> Path:
    meta, body = parse_frontmatter(content)
    if meta.spek.template == "jinja":
        body = _apply_jinja(
            body,
            {
                "modules": set(modules or []),
                "integrations": set(integrations or []),
            },
        )
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
        if meta.spek.preapproved_tools:
            existing = fm.get("allowed-tools", [])
            fm["allowed-tools"] = existing + [t for t in meta.spek.preapproved_tools if t not in existing]
        if meta.spek.integrations:
            claude_meta = {k: v for k, v in meta.spek.integrations.get("claude", {}).items() if k not in ("hooks", "allowed-tools")}
            fm.update(claude_meta)
            extra_tools = meta.spek.integrations.get("claude", {}).get("allowed-tools", [])
            if extra_tools:
                existing = fm.get("allowed-tools", [])
                fm["allowed-tools"] = existing + [t for t in extra_tools if t not in existing]
            if claude_meta.get("context") == "fork":
                existing = fm.get("allowed-tools", [])
                injected = ["Bash(test .spek/STRUCTURE.md)", "Bash(cat .spek/STRUCTURE.md)"]
                fm["allowed-tools"] = existing + [t for t in injected if t not in existing]
                body = body.rstrip("\n") + "\n\n## Project structure\n\n!`test -f .spek/STRUCTURE.md && cat .spek/STRUCTURE.md`\n"
        out_path = skill_dir / "SKILL.md"
        out_path.write_text(f"---\n{dump_yaml(fm)}\n---\n{body}")
        return out_path

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (stem + ".md")
    out_path.write_text(body)
    return out_path
