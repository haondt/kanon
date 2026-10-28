from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, override

from pydantic import BaseModel, Field

from kanon.core.config import (
    PROJECT_KANON_DIR,
    Integration,
    KanonConfig,
    OutputType,
    SourcedResource,
)
from kanon.core.errors import KanonRuntimeError
from kanon.core.kanons import Kanon
from kanon.core.ledger import LEDGER_FILE, Ledger, check_json_file_readable
from kanon.core.render._base import DryCleanResult, GlobalKanonRenderer, KanonRenderHelper, SkillDirectoryConflictError
from kanon.core.yaml_utils import dump_yaml, save_json

_RULE_OUTPUT_DIR = ".claude/rules"
_SKILL_OUTPUT_DIR = ".claude/skills"
_SETTINGS_FILE = ".claude/settings.json"
_GLOBAL_RULE_SUBDIR = "kanon"
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


_SKILL_COLLISION_PREFIX = "kanon--"


def _ledger() -> Ledger:
    return Ledger.load(KanonConfig.root() / LEDGER_FILE)


def _claim_skill_dir(skills_dir: Path, name: str, on_progress: Callable[[str], None] | None = None) -> Path:
    """Pick and record the directory for skill `name`: plain if free or already ours, `kanon--` prefixed if a foreign skill holds it."""
    ledger = _ledger()
    for dirname in (name, f"{_SKILL_COLLISION_PREFIX}{name}"):
        if ledger.has_blob(ClaudeKanonRenderer.INTEGRATION, skills_dir / dirname):
            return skills_dir / dirname

    dirname = name
    if (skills_dir / dirname).exists():
        dirname = f"{_SKILL_COLLISION_PREFIX}{name}"
        if (skills_dir / dirname).exists():
            raise SkillDirectoryConflictError(
                f"cannot install skill '{name}': both {skills_dir / name} and {skills_dir / dirname} exist and are not managed by kanon"
            )
    ledger.claim_blob(ClaudeKanonRenderer.INTEGRATION, skills_dir / dirname, "directory", on_progress)
    return skills_dir / dirname


@dataclass
class ClaudeKanonRenderer(GlobalKanonRenderer):
    INTEGRATION: Integration = Integration.CLAUDE
    @classmethod
    @override
    def global_root(cls) -> Path:
        return Path.home()

    @classmethod
    @override
    def render_kanon(
        cls,
        kanon_resource: SourcedResource,
        kanon: Kanon,
        on_progress: Callable[[str], None] | None = None,
    ) -> Path:
        helper = KanonRenderHelper(kanon=kanon, resource=kanon_resource).validate()

        body = helper.base_render_body()

        skill_preapproved_tools: set[str] = set(helper.meta.preapproved_tools)
        if helper.meta.output == OutputType.SKILL:
            out_dir = cls.output_root() / _SKILL_OUTPUT_DIR
            frontmatter = ClaudeSkillFrontmatter(
                name=helper.name,
                description=helper.meta.description,
                argument_hint=helper.meta.skill.args,
            )

            if helper.meta.skill.model_invokable == False:
                frontmatter.disable_model_invocation = True

            if not helper.meta.skill.needs_context:
                if not KanonConfig.is_global():
                    skill_preapproved_tools = skill_preapproved_tools | {
                        f"Bash(test {PROJECT_KANON_DIR}/STRUCTURE.md)",
                        f"Bash(cat {PROJECT_KANON_DIR}/STRUCTURE.md)",
                    }
                    body = (
                        body.rstrip("\n")
                        + f"\n\n## Project structure\n\n!`test -f {PROJECT_KANON_DIR}/STRUCTURE.md && cat {PROJECT_KANON_DIR}/STRUCTURE.md`\n"
                    )
                frontmatter.context = "fork"
                if skill_preapproved_tools:
                    frontmatter.allowed_tools = list(skill_preapproved_tools)

            if KanonConfig.is_global():
                skill_dir = _claim_skill_dir(out_dir, helper.name, on_progress)
            else:
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
        out_dir = cls.output_root() / _RULE_OUTPUT_DIR
        if KanonConfig.is_global():
            out_dir = out_dir / _GLOBAL_RULE_SUBDIR
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
        root = cls.output_root()
        if KanonConfig.is_global():
            skill_dirs = _ledger().owned_blobs(ClaudeKanonRenderer.INTEGRATION, "directory")
            return DryCleanResult(
                directories=[root / _RULE_OUTPUT_DIR / _GLOBAL_RULE_SUBDIR, *skill_dirs],
                extra_info=f"Will rewind kanon-managed entries in {root / _SETTINGS_FILE}",
            )
        return DryCleanResult(
            files=[root / _SETTINGS_FILE],
            directories=[root / _RULE_OUTPUT_DIR, root / _SKILL_OUTPUT_DIR]
        )

    @override
    @classmethod
    def clean(cls, on_clean_progress: Callable[[str], None] | None = None):
        is_global = KanonConfig.is_global()
        if is_global:
            check_json_file_readable(cls.output_root() / _SETTINGS_FILE)
        super().clean(on_clean_progress)
        if is_global:
            _ledger().release_blobs(ClaudeKanonRenderer.INTEGRATION, "directory")
            _ledger().rewind_json(ClaudeKanonRenderer.INTEGRATION, cls.output_root() / _SETTINGS_FILE, on_clean_progress)

    @override
    @classmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
        on_progress: Callable[[str], None] | None = None,
    ) -> Path:
        settings_path = cls.output_root() / _SETTINGS_FILE
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        if KanonConfig.is_global():
            desired: dict[str, Any] = {"includeGitInstructions": False}
            if preapproved_tools:
                desired["permissions"] = {"allow": preapproved_tools}
            _ledger().apply_json(ClaudeKanonRenderer.INTEGRATION, settings_path, desired, on_progress)
            return settings_path
        settings_object = _ADDITIONAL_SETTINGS.copy()
        if preapproved_tools:
            settings_object["permissions"] = {"allow": preapproved_tools}
        save_json(settings_object, settings_path)
        return settings_path
