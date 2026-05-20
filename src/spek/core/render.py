from __future__ import annotations

import re
import yaml
from pathlib import Path

# Per tool: maps output type → relative directory.
# "stance" is tool-independent — always goes to .spek/stances/.
AI_TOOL_OUTPUT_DIRS: dict[str, dict[str, str]] = {
    "claude": {
        "rule": ".claude/rules",
        "command": ".claude/commands",
    },
    "windsurf": {
        "rule": ".windsurf/rules",
        "command": ".windsurf/rules",
    },
}

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body without frontmatter block)."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    meta = yaml.safe_load(match.group(1)) or {}
    body = content[match.end():]
    return meta, body


def output_type(content: str) -> str:
    """Return 'command' or 'rule' based on spec frontmatter."""
    meta, _ = parse_frontmatter(content)
    return meta.get("spek", {}).get("output", "rule")


def output_dir_for(project_root: Path, ai_tool: str, out_type: str) -> Path:
    tool_dirs = AI_TOOL_OUTPUT_DIRS.get(ai_tool)
    if tool_dirs is None:
        raise ValueError(f"Unknown ai_tool '{ai_tool}'. Supported: {list(AI_TOOL_OUTPUT_DIRS)}")
    rel = tool_dirs.get(out_type, tool_dirs["rule"])
    return project_root / rel


def render_module(content: str, module: str, ai_tool: str, project_root: Path) -> Path:
    """Parse frontmatter, route to correct output dir, strip frontmatter, write file."""
    _, body = parse_frontmatter(content)
    out_type = output_type(content)
    out_dir = output_dir_for(project_root, ai_tool, out_type)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = module.replace("/", "-") + ".md"
    out_path = out_dir / filename
    out_path.write_text(body)
    return out_path
