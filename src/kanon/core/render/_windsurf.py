from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, override

from pydantic import BaseModel

from kanon.core.config import IntegrationSpecificRule, KanonConfig, OutputType, SourceReference, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, KanonRenderHelper, KanonRenderer
from kanon.core.yaml_utils import dump_yaml

_RULE_OUTPUT_DIR = ".windsurf/rules"
_SKILL_OUTPUT_DIR = ".windsurf/workflows"
_SPECIFIC_RULES = [
    IntegrationSpecificRule(
        path="windsurf-rules",
        frontmatter={"trigger": "always_on"},
        content="""## Project structure
- CRITICAL: The first action in every conversation is reading @.kanon/STRUCTURE.md. Do not respond to the user, write any files or plan any actions until this is complete.
- When running shell commands, prefer using the bash tool over interactive shell execution for better syntax highlighting in the chat window.
- Run `kanon` commands via blocking `run_command` calls; never background + `command_status`.""",
    )
]


class WindsurfRuleFrontmatter(BaseModel):
    trigger: str = "always_on"


class WindsurfSkillFrontmatter(BaseModel):
    description: str | None = None


@dataclass
class WindsurfKanonRenderer(KanonRenderer):
    @classmethod
    def _get_rule_output_dir(cls) -> str:
        return _RULE_OUTPUT_DIR

    @classmethod
    def _get_skill_output_dir(cls) -> str:
        return _SKILL_OUTPUT_DIR

    @classmethod
    def _get_specific_rules(cls) -> list[IntegrationSpecificRule]:
        return _SPECIFIC_RULES

    @classmethod
    @override
    def render_kanon(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Path:
        helper = KanonRenderHelper(kanon=kanon, resource=kanon_resource).validate()
        body = helper.base_render_body()
        out_dir = (
            KanonConfig.project_root()
            / (
                cls._get_skill_output_dir()
                if helper.meta.output == OutputType.SKILL
                else cls._get_rule_output_dir()
            )
        )

        if helper.meta.output == OutputType.SKILL:
            frontmatter = WindsurfSkillFrontmatter(description=helper.meta.description)
            out_path = out_dir / Path(helper.name).with_suffix(".md")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path
        return cls.render_rule(
            helper.resource, WindsurfRuleFrontmatter(), body
        )

    @override
    @classmethod
    def render_rule(
        cls,
        resource: SourcedResource,
        frontmatter: dict[str, Any] | BaseModel | None,
        content: str,
    ) -> Path:
        out_dir = KanonConfig.project_root() / cls._get_rule_output_dir()
        path_infix = f"{resource.source.cache_subpath()}/{resource.path}"
        flattened = path_infix.replace("/", "--")
        out_path = out_dir / Path(flattened).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{content}")
        else:
            out_path.write_text(content)
        return out_path

    @override
    @classmethod
    def render_bespoke_rules(cls,
        on_render_progress: Callable[[Path], None] | None = None
    ):
        for rule in cls._get_specific_rules():
            resource = SourcedResource(SourceReference.KANON_SOURCE_REFERENCE, path=rule.path, args=rule.args)
            out_path = cls.render_rule(resource, rule.frontmatter, rule.content)
            if on_render_progress:
                on_render_progress(out_path)

    @override
    @classmethod
    def dry_clean(cls) -> DryCleanResult:
        project_root = KanonConfig.project_root()
        return DryCleanResult(
            directories=[
                project_root / cls._get_rule_output_dir(),
                project_root / cls._get_skill_output_dir(),
            ],
        )

    @override
    @classmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
    ) -> Path | None:
        return None
