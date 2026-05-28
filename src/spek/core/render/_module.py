from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Self, override

import jinja2
from pydantic import BaseModel, Field

from spek.core.config import AI_TOOL_OUTPUT_DIRS, PROJECT_SPEK_DIR, Integration, OutputType, SourcedResource, SpekConfig
from spek.core.modules import Module
from spek.core.yaml_utils import dump_yaml


def _apply_jinja(body: str, context: dict[str, Any]) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, keep_trailing_newline=True)
    return env.from_string(body).render(**context)


def output_dir_for(integration: Integration, out_type: OutputType) -> Path:
    tool_dirs = AI_TOOL_OUTPUT_DIRS[integration]
    rel = tool_dirs.get(out_type, tool_dirs[OutputType.RULE])
    return SpekConfig.project_root() / rel


@dataclass
class ModuleRenderer(ABC):
    module: Module
    resource: SourcedResource

    @cached_property
    def _meta(self):
        return self.module.frontmatter.spek

    def _name(self):
        return self._meta.name or self.resource.as_string

    def _output_path_infix(self):
        return f"{self.resource.source.scheme}/{self.resource.source.address}/{self.resource.path}"

    def _validate(self):
        if self._meta.output == OutputType.SKILL and not self._meta.name:
            raise ValueError(
                f"Skill module '{self.resource.as_string}' is missing spek.name — skills require an explicit name"
            )
    def _base_render_body(self):
        config = SpekConfig.instance()
        if self._meta.template == "jinja":
            return _apply_jinja(self.module.content, {"modules": config.modules, "integrations": config.meta.integrations})
        return self.module.content

    @abstractmethod
    def render(self) -> Path:
        ...
    @classmethod
    @abstractmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        ...

    @classmethod
    @abstractmethod
    def create(cls, module_resource: SourcedResource, module: Module) -> Self:
        ...


class ClaudeSkillFrontmatter(BaseModel):
    name: str | None = None
    description: str | None = None
    argument_hint: str | None = Field(serialization_alias='argument-hint', default=None)
    disable_model_invocation: bool | None = Field(serialization_alias='disable-model-invocation', default=None)
    context: str | None = None
    allowed_tools: list[str] | None = Field(serialization_alias='allowed-tools', default=None)

@dataclass
class ClaudeModuleRenderer(ModuleRenderer):

    @classmethod
    @override
    def create(cls, module_resource: SourcedResource, module: Module) -> Self:
        renderer = cls(
            module=module,
            resource=module_resource
        )

        renderer._validate()
        return renderer

    @override
    def render(self) -> Path:
        body = self._base_render_body()

        skill_preapproved_tools: set[str] = set(self._meta.preapproved_tools)
        if not self._meta.needs_context:
            skill_preapproved_tools = skill_preapproved_tools | {f"Bash(test {PROJECT_SPEK_DIR}/STRUCTURE.md)", f"Bash(cat {PROJECT_SPEK_DIR}/STRUCTURE.md)"}
            body = body.rstrip("\n") + f"\n\n## Project structure\n\n!`test -f {PROJECT_SPEK_DIR}/STRUCTURE.md && cat {PROJECT_SPEK_DIR}/STRUCTURE.md`\n"

        out_dir=output_dir_for(Integration.CLAUDE, self._meta.output)
        if self._meta.output == OutputType.SKILL:

            frontmatter = ClaudeSkillFrontmatter(
                name=self._name(),
                description=self._meta.description,
                argument_hint=self._meta.skill.args,
            )

            if self._meta.skill.model_invokable == False:
                frontmatter.disable_model_invocation = True

            if self._meta.skill.needs_context == False:
                frontmatter.context = "fork"
                frontmatter.allowed_tools = list(skill_preapproved_tools)

            skill_dir = out_dir / self._name()
            skill_dir.mkdir(parents=True, exist_ok=True)
            out_path = skill_dir / "SKILL.md"
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{body}")
            return out_path

        else:
            return ClaudeModuleRenderer.render_rule(self.resource, None, body)

    @override
    @classmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        out_dir = output_dir_for(Integration.CLAUDE, OutputType.RULE)
        out_path = (out_dir / f"{resource.source.scheme}/{resource.source.address}/{resource.path}").with_suffix(".md")
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
class WindsurfModuleRenderer(ModuleRenderer):

    @classmethod
    @override
    def create(cls, module_resource: SourcedResource, module: Module) -> Self:
        renderer = cls(
            module=module,
            resource=module_resource,
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
            return WindsurfModuleRenderer.render_rule(
                self.resource,
                WindsurfRuleFrontmatter(),
                body
            )

    @override
    @classmethod
    def render_rule(cls, resource: SourcedResource, frontmatter: dict[str, Any] | BaseModel | None, content: str) -> Path:
        out_dir = output_dir_for(Integration.WINDSURF, OutputType.RULE)
        path_infix = f"{resource.source.scheme}/{resource.source.address}/{resource.path}"
        flattened = path_infix.replace("/", "--")
        out_path = out_dir / Path(flattened).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            out_path.write_text(f"---\n{dump_yaml(frontmatter)}\n---\n{content}")
        else:
            out_path.write_text(content)
        return out_path

_RENDERERS: dict[Integration, type[ModuleRenderer]] = {
    Integration.CLAUDE: ClaudeModuleRenderer,
    Integration.WINDSURF: WindsurfModuleRenderer,
}

def render_rule(
    resource: SourcedResource,
    frontmatter: dict[str, Any],
    content: str,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].render_rule(resource, frontmatter, content)

def render_module(
    module_resource: SourcedResource,
    module: Module,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].create(module_resource, module).render()
