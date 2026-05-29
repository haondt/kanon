from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field

from spek.core.config import OutputType
from spek.core.yaml_utils import FRONTMATTER_RE, dump_yaml, parse_yaml

from typing import Any, Literal


class _SkillMeta(BaseModel):
    model_invokable: bool = True
    human_invokable: bool = True
    args: str | None = None
    needs_context: bool = True

class _SpekMeta(BaseModel):
    output: OutputType = Field(default=OutputType.RULE)
    name: str | None = None
    description: str | None = None
    skill: _SkillMeta = Field(default_factory=_SkillMeta)
    preapproved_tools: list[str] = Field(default_factory=list)
    template: Literal["jinja"] | None = None

class ModuleFrontmatter(BaseModel):
    spek: _SpekMeta = _SpekMeta()

@dataclass
class Module:
    frontmatter: ModuleFrontmatter
    content: str

    @property
    def description(self) -> str | None:
        return self.frontmatter.spek.description

    @classmethod
    def load(cls, content: str) -> Module:
        if fm_match := FRONTMATTER_RE.match(content):
            data: dict[str, Any] = parse_yaml(fm_match.group(1))
            fm = ModuleFrontmatter.model_validate(data)
            content = content[fm_match.end():]
        else:
            fm = ModuleFrontmatter()
        return cls(frontmatter=fm, content=content)

    def dump(self) -> str:
        if self.frontmatter == ModuleFrontmatter():
            return self.content
        return f"---\n{dump_yaml(self.frontmatter)}---\n{self.content}"

