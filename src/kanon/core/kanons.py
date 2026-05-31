from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field

from kanon.core.config import OutputType
from kanon.core.yaml_utils import FRONTMATTER_RE, dump_yaml, parse_yaml

from typing import Any, Literal


class _SkillMeta(BaseModel):
    model_invokable: bool = True
    human_invokable: bool = True
    args: str | None = None
    needs_context: bool = True

class _KanonMeta(BaseModel):
    output: OutputType = Field(default=OutputType.RULE)
    name: str | None = None
    description: str | None = None
    skill: _SkillMeta = Field(default_factory=_SkillMeta)
    preapproved_tools: list[str] = Field(default_factory=list)
    template: Literal["jinja"] | None = None

class KanonFrontmatter(BaseModel):
    kanon: _KanonMeta = _KanonMeta()

@dataclass
class Kanon:
    frontmatter: KanonFrontmatter
    content: str

    @property
    def description(self) -> str | None:
        return self.frontmatter.kanon.description

    @classmethod
    def load(cls, content: str) -> Kanon:
        if fm_match := FRONTMATTER_RE.match(content):
            data: dict[str, Any] = parse_yaml(fm_match.group(1))
            fm = KanonFrontmatter.model_validate(data)
            content = content[fm_match.end():]
        else:
            fm = KanonFrontmatter()
        return cls(frontmatter=fm, content=content)

    def dump(self) -> str:
        if self.frontmatter == KanonFrontmatter():
            return self.content
        return f"---\n{dump_yaml(self.frontmatter)}---\n{self.content}"

