from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from spek.core.yaml_utils import FRONTMATTER_RE, dump_yaml, parse_yaml

AI_TOOL_OUTPUT_DIRS: dict[str, dict[str, str]] = {
    "claude": {
        "rule": ".claude/rules",
        "command": ".claude/skills",
    },
    "windsurf": {
        "rule": ".windsurf/rules",
        "command": ".windsurf/rules",
    },
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

    if out_type == "command" and ai_tool == "claude":
        skill_dir = out_dir / stem
        skill_dir.mkdir(parents=True, exist_ok=True)
        fm: dict[str, Any] = {}
        fm["name"] = stem
        if meta.spek.description:
            fm["description"] = meta.spek.description
        if meta.spek.args:
            fm["argument-hint"] = meta.spek.args
        if meta.spek.integrations:
            fm.update(meta.spek.integrations.get("claude", {}))
        out_path = skill_dir / "SKILL.md"
        out_path.write_text(f"---\n{dump_yaml(fm)}\n---\n{body}")
        return out_path

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (stem + ".md")
    out_path.write_text(body)
    return out_path
