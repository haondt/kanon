from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Self, override

import jinja2
from pydantic import BaseModel, Field

from kanon.core.config import AI_TOOL_OUTPUT_DIRS, PROJECT_KANON_DIR, Integration, OutputType, SourcedResource, KanonConfig
from kanon.core.kanons import Kanon
from kanon.core.yaml_utils import dump_yaml


def _apply_jinja(body: str, context: dict[str, Any]) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, keep_trailing_newline=True)
    return env.from_string(body).render(**context)


def output_dir_for(integration: Integration, out_type: OutputType) -> Path:
    tool_dirs = AI_TOOL_OUTPUT_DIRS[integration]
    rel = tool_dirs.get(out_type, tool_dirs[OutputType.RULE])
    return KanonConfig.project_root() / rel


@dataclass
class KanonRenderer(ABC):
    kanon: Kanon
    resource: SourcedResource

    @cached_property
    def _meta(self):
        return self.kanon.frontmatter.kanon

    def _name(self):
        return self._meta.name or self.resource.as_string

    def _output_path_infix(self):
        return f"{self.resource.source.scheme}/{self.resource.source.address}/{self.resource.path}"

    def _validate(self):
        if self._meta.output == OutputType.SKILL and not self._meta.name:
            raise ValueError(
                f"Skill kanon '{self.resource.as_string}' is missing kanon.name — skills require an explicit name"
            )
    def _base_render_body(self):
        config = KanonConfig.instance()
        if self._meta.template == "jinja":
            return _apply_jinja(self.kanon.content, {"kanons": config.kanons, "integrations": config.meta.integrations})
        return self.kanon.content

    @abstractmethod
    def render(self) -> Path:
        ...
    @classmethod
    @abstractmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        ...

    @classmethod
    @abstractmethod
    def create(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Self:
        ...


class ClaudeSkillFrontmatter(BaseModel):
    name: str | None = None
    description: str | None = None
    argument_hint: str | None = Field(serialization_alias='argument-hint', default=None)
    disable_model_invocation: bool | None = Field(serialization_alias='disable-model-invocation', default=None)
    context: str | None = None
    allowed_tools: list[str] | None = Field(serialization_alias='allowed-tools', default=None)

@dataclass
class ClaudeKanonRenderer(KanonRenderer):

    @classmethod
    @override
    def create(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Self:
        renderer = cls(
            kanon=kanon,
            resource=kanon_resource
        )

        renderer._validate()
        return renderer

    @override
    def render(self) -> Path:
        body = self._base_render_body()

        skill_preapproved_tools: set[str] = set(self._meta.preapproved_tools)
        out_dir = output_dir_for(Integration.CLAUDE, self._meta.output)
        if self._meta.output == OutputType.SKILL:

            frontmatter = ClaudeSkillFrontmatter(
                name=self._name(),
                description=self._meta.description,
                argument_hint=self._meta.skill.args,
            )

            if self._meta.skill.model_invokable == False:
                frontmatter.disable_model_invocation = True

            if not self._meta.skill.needs_context:
                skill_preapproved_tools = skill_preapproved_tools | {f"Bash(test {PROJECT_KANON_DIR}/STRUCTURE.md)", f"Bash(cat {PROJECT_KANON_DIR}/STRUCTURE.md)"}
                body = body.rstrip("\n") + f"\n\n## Project structure\n\n!`test -f {PROJECT_KANON_DIR}/STRUCTURE.md && cat {PROJECT_KANON_DIR}/STRUCTURE.md`\n"
                frontmatter.context = "fork"
                frontmatter.allowed_tools = list(skill_preapproved_tools)

            skill_dir = out_dir / self._name()
            skill_dir.mkdir(parents=True, exist_ok=True)
            out_path = skill_dir / "SKILL.md"
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path

        else:
            return ClaudeKanonRenderer.render_rule(self.resource, None, body)

    @override
    @classmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        out_dir = output_dir_for(Integration.CLAUDE, OutputType.RULE)
        out_path = (out_dir / resource.source.cache_subpath() / resource.path).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{content}")
        else:
            out_path.write_text(content)
        return out_path


class WindsurfRuleFrontmatter(BaseModel):
    trigger: str = "always_on"


class WindsurfSkillFrontmatter(BaseModel):
    description: str | None = None


@dataclass
class WindsurfKanonRenderer(KanonRenderer):

    @classmethod
    @override
    def create(cls, kanon_resource: SourcedResource, kanon: Kanon) -> Self:
        renderer = cls(
            kanon=kanon,
            resource=kanon_resource,
        )
        renderer._validate()
        return renderer

    @override
    def render(self) -> Path:
        body = self._base_render_body()
        out_dir = output_dir_for(Integration.WINDSURF, self._meta.output)

        if self._meta.output == OutputType.SKILL:
            frontmatter = WindsurfSkillFrontmatter(description=self._meta.description)
            out_path = out_dir / Path(self._name()).with_suffix(".md")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path
        else:
            return WindsurfKanonRenderer.render_rule(
                self.resource,
                WindsurfRuleFrontmatter(),
                body
            )

    @override
    @classmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        out_dir = output_dir_for(Integration.WINDSURF, OutputType.RULE)
        path_infix = f'{resource.source.cache_subpath()}/{resource.path}'
        flattened = path_infix.replace("/", "--")
        out_path = out_dir / Path(flattened).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{content}")
        else:
            out_path.write_text(content)
        return out_path

_RENDERERS: dict[Integration, type[KanonRenderer]] = {
    Integration.CLAUDE: ClaudeKanonRenderer,
    Integration.WINDSURF: WindsurfKanonRenderer,
}

def render_rule(
    resource: SourcedResource,
    frontmatter: dict[str, Any],
    content: str,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].render_rule(resource, frontmatter, content)

def render_kanon(
    kanon_resource: SourcedResource,
    kanon: Kanon,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].create(kanon_resource, kanon).render()
