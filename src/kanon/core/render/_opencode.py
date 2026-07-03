from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, override

from pydantic import BaseModel

from kanon.core.config import KanonConfig, OutputType, PROJECT_KANON_DIR, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, KanonRenderHelper, KanonRenderer
from kanon.core.yaml_utils import dump_yaml, save_json

_RULE_OUTPUT_DIR = ".opencode/rules"
_SKILL_OUTPUT_DIR = ".opencode/skills"
_SETTINGS_FILE = "opencode.json"
_ADDITIONAL_SETTINGS: dict[str, Any] = {
    "$schema": "https://opencode.ai/config.json",
    "instructions": [
        f"{PROJECT_KANON_DIR}/STRUCTURE.md",
        ".opencode/rules/**/*.md",
    ],
}


class OpenCodeSkillFrontmatter(BaseModel):
    name: str
    description: str | None = None
    license: str | None = None
    compatibility: str | None = None
    metadata: dict[str, str] | None = None


@dataclass
class OpenCodeKanonRenderer(KanonRenderer):
    @classmethod
    @override
    def render_kanon(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Path:
        helper = KanonRenderHelper(kanon=kanon, resource=kanon_resource).validate()
        body = helper.base_render_body()
        if helper.meta.output == OutputType.SKILL:
            out_dir = KanonConfig.project_root() / _SKILL_OUTPUT_DIR
            frontmatter = OpenCodeSkillFrontmatter(
                name=helper.name,
                description=helper.meta.description,
            )
            skill_dir = out_dir / helper.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            out_path = skill_dir / "SKILL.md"
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path
        return OpenCodeKanonRenderer.render_rule(helper.resource, None, body)

    @override
    @classmethod
    def render_rule(
        cls,
        resource: SourcedResource,
        frontmatter: dict[str, Any] | BaseModel | None,
        content: str,
    ) -> Path:
        out_dir = KanonConfig.project_root() / _RULE_OUTPUT_DIR
        out_path = (
            out_dir / resource.source.cache_subpath() / resource.path
        ).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{content}")
        else:
            out_path.write_text(content)
        return out_path

    @override
    @classmethod
    def dry_clean(cls) -> DryCleanResult:
        project_root = KanonConfig.project_root()
        return DryCleanResult(
            files=[project_root / _SETTINGS_FILE],
            directories=[
                project_root / _RULE_OUTPUT_DIR,
                project_root / _SKILL_OUTPUT_DIR,
            ],
        )

    @override
    @classmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
    ) -> Path:
        settings_path = KanonConfig.project_root() / _SETTINGS_FILE
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(_ADDITIONAL_SETTINGS.copy(), settings_path)
        return settings_path
