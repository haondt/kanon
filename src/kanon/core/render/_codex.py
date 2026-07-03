from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, override

from pydantic import BaseModel

from kanon.core.config import (
    IntegrationSpecificRule,
    KanonConfig,
    OutputType,
    SourceReference,
    SourcedResource,
)
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, KanonRenderHelper, KanonRenderer
from kanon.core.yaml_utils import dump_yaml

_SKILL_OUTPUT_DIR = ".agents/skills"
_SPECIFIC_RULES = [
    IntegrationSpecificRule(
        path="codex-rules",
        content="""## Project structure
- CRITICAL: The first action in every conversation is reading `.kanon/STRUCTURE.md` if it exists. Do not respond to the user, write any files, or plan any actions until this is complete.""",
    )
]

_CODEX_AGENTS_FILE = "AGENTS.md"
_CODEX_MANAGED_BLOCK_START = "<!-- kanon:codex:start -->"
_CODEX_MANAGED_BLOCK_END = "<!-- kanon:codex:end -->"


class CodexSkillFrontmatter(BaseModel):
    name: str
    description: str | None = None


@dataclass
class CodexKanonRenderer(KanonRenderer):
    @classmethod
    def _agents_path(cls) -> Path:
        return KanonConfig.project_root() / _CODEX_AGENTS_FILE

    @classmethod
    def _strip_managed_agents_block(cls, text: str) -> str:
        start = text.find(_CODEX_MANAGED_BLOCK_START)
        end = text.find(_CODEX_MANAGED_BLOCK_END)
        if start == -1 or end == -1 or end < start:
            return text.rstrip()
        end += len(_CODEX_MANAGED_BLOCK_END)
        before = text[:start].rstrip()
        after = text[end:].lstrip()
        if before and after:
            return f"{before}\n\n{after.rstrip()}"
        return before or after.rstrip()

    @classmethod
    def _clear_managed_agents_block(cls) -> None:
        path = cls._agents_path()
        if not path.exists():
            return

        retained = cls._strip_managed_agents_block(path.read_text())
        if retained:
            path.write_text(retained.rstrip() + "\n")
        else:
            path.unlink()

    @classmethod
    def _append_managed_agents_block(cls, content: str) -> Path:
        path = cls._agents_path()
        existing = path.read_text() if path.exists() else ""

        start = existing.find(_CODEX_MANAGED_BLOCK_START)
        end = existing.find(_CODEX_MANAGED_BLOCK_END)
        entry = content.rstrip() + "\n"
        if start != -1 and end != -1 and start < end:
            insert_at = end
            updated = existing[:insert_at].rstrip() + "\n\n" + entry + existing[insert_at:]
        else:
            base = existing.rstrip()
            prefix = (base + "\n\n") if base else ""
            updated = (
                prefix
                + _CODEX_MANAGED_BLOCK_START
                + "\n"
                + "# Kanon Instructions\n\n"
                + entry
                + _CODEX_MANAGED_BLOCK_END
                + "\n"
            )

        path.write_text(updated)
        return path

    @classmethod
    @override
    def render_kanon(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Path:
        helper = KanonRenderHelper(kanon=kanon, resource=kanon_resource).validate()
        body = helper.base_render_body()
        if helper.meta.output == OutputType.SKILL:
            out_dir = KanonConfig.project_root() / _SKILL_OUTPUT_DIR
            skill_dir = out_dir / helper.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            out_path = skill_dir / "SKILL.md"
            frontmatter = CodexSkillFrontmatter(
                name=helper.name,
                description=helper.meta.description,
            )
            out_path.write_text("---\n" + dump_yaml(frontmatter) + "---\n" + body)
            return out_path
        return CodexKanonRenderer.render_rule(helper.resource, None, body)

    @override
    @classmethod
    def render_rule(
        cls,
        resource: SourcedResource,
        frontmatter: dict[str, Any] | BaseModel | None,
        content: str,
    ) -> Path:
        heading = resource.as_string
        if frontmatter:
            rendered = f"## {heading}\n\n---\n{dump_yaml(frontmatter)}\n---\n{content}"
        else:
            rendered = f"## {heading}\n\n{content}"
        return cls._append_managed_agents_block(rendered)

    @override
    @classmethod
    def render_bespoke_rules(cls,
        on_render_progress: Callable[[Path], None] | None = None
    ):
        for rule in _SPECIFIC_RULES:
            resource = SourcedResource(SourceReference.KANON_SOURCE_REFERENCE, path=rule.path, args=rule.args)
            out_path = cls.render_rule(resource, rule.frontmatter, rule.content)
            if on_render_progress:
                on_render_progress(out_path)

    @override
    @classmethod
    def dry_clean(cls) -> DryCleanResult:
        return DryCleanResult(
            directories=[KanonConfig.project_root() / _SKILL_OUTPUT_DIR],
            extra_info="remove managed kanon block from AGENTS.md",
        )

    @override
    @classmethod
    def clean(cls, on_clean_progress: Callable[[str], None] | None = None):
        super().clean(on_clean_progress)
        cls._clear_managed_agents_block()
        if on_clean_progress:
            on_clean_progress("  removed AGENTS.md managed block")

    @override
    @classmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
    ) -> Path | None:
        return None
