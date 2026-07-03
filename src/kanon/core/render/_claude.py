from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, override

from pydantic import BaseModel, Field

from kanon.core.config import (
    PROJECT_KANON_DIR,
    KanonConfig,
    OutputType,
    SourcedResource,
)
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, KanonRenderHelper, KanonRenderer
from kanon.core.yaml_utils import dump_yaml, save_json

_RULE_OUTPUT_DIR = ".claude/rules"
_SKILL_OUTPUT_DIR = ".claude/skills"
_SETTINGS_FILE = ".claude/settings.json"
_ADDITIONAL_SETTINGS: dict[str, Any] = {
    "includeGitInstructions": False,
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash -c 'test -f {PROJECT_KANON_DIR}/STRUCTURE.md && cat {PROJECT_KANON_DIR}/STRUCTURE.md'",
                    }
                ],
            },
            {
                "matcher": "clear",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash -c 'test -f {PROJECT_KANON_DIR}/STRUCTURE.md && cat {PROJECT_KANON_DIR}/STRUCTURE.md'",
                    }
                ],
            },
        ]
    },
}


class ClaudeSkillFrontmatter(BaseModel):
    name: str | None = None
    description: str | None = None
    argument_hint: str | None = Field(serialization_alias="argument-hint", default=None)
    disable_model_invocation: bool | None = Field(
        serialization_alias="disable-model-invocation", default=None
    )
    context: str | None = None
    allowed_tools: list[str] | None = Field(
        serialization_alias="allowed-tools", default=None
    )


@dataclass
class ClaudeKanonRenderer(KanonRenderer):
    @classmethod
    @override
    def render_kanon(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Path:
        helper = KanonRenderHelper(kanon=kanon, resource=kanon_resource).validate()

        body = helper.base_render_body()

        skill_preapproved_tools: set[str] = set(helper.meta.preapproved_tools)
        if helper.meta.output == OutputType.SKILL:
            out_dir = KanonConfig.project_root() / _SKILL_OUTPUT_DIR
            frontmatter = ClaudeSkillFrontmatter(
                name=helper.name,
                description=helper.meta.description,
                argument_hint=helper.meta.skill.args,
            )

            if helper.meta.skill.model_invokable == False:
                frontmatter.disable_model_invocation = True

            if not helper.meta.skill.needs_context:
                skill_preapproved_tools = skill_preapproved_tools | {
                    f"Bash(test {PROJECT_KANON_DIR}/STRUCTURE.md)",
                    f"Bash(cat {PROJECT_KANON_DIR}/STRUCTURE.md)",
                }
                body = (
                    body.rstrip("\n")
                    + f"\n\n## Project structure\n\n!`test -f {PROJECT_KANON_DIR}/STRUCTURE.md && cat {PROJECT_KANON_DIR}/STRUCTURE.md`\n"
                )
                frontmatter.context = "fork"
                frontmatter.allowed_tools = list(skill_preapproved_tools)

            skill_dir = out_dir / helper.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            out_path = skill_dir / "SKILL.md"
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path

        return ClaudeKanonRenderer.render_rule(helper.resource, None, body)

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
            directories=[project_root / _RULE_OUTPUT_DIR, project_root / _SKILL_OUTPUT_DIR]
        )

    @override
    @classmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
    ) -> Path:
        settings_path = KanonConfig.project_root() / _SETTINGS_FILE
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_object = _ADDITIONAL_SETTINGS.copy()
        if preapproved_tools:
            settings_object["permissions"] = {"allow": preapproved_tools}
        save_json(settings_object, settings_path)
        return settings_path
