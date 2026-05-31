from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, field_validator

from kanon.core.yaml_utils import FRONTMATTER_RE, parse_yaml

@dataclass
class NormalizedTerms:
    terms: list[str]
    def __post_init__(self):
        self.terms = list({i.strip().lower() for i in self.terms})
    def __len__(self) -> int:
        return len(self.terms)

class ReferenceMeta(BaseModel):
    description: str | None = None
    keywords: list[str] = []

    @field_validator("keywords", mode="before")
    @classmethod
    def normalize_keywords(cls, v: list[str]) -> list[str]:
        return list(set([i.strip().lower() for i in v]))

class ReferenceFrontmatter(BaseModel):
    kanon: ReferenceMeta = ReferenceMeta()

class Reference(BaseModel):
    frontmatter: ReferenceFrontmatter
    content: str | None = None
    path: str

    @classmethod
    def load(cls, path: str, content: str) -> Reference:
        fm_match = FRONTMATTER_RE.match(content)
        if not fm_match:
            fm = ReferenceFrontmatter()
        else:
            data: dict[str, Any] = parse_yaml(fm_match.group(1))
            fm = ReferenceFrontmatter.model_validate(data)
            content = content[fm_match.end():]
        return cls(frontmatter=fm, content=content, path=path)

    def score(self, terms: NormalizedTerms) -> int:
        return sum(1 for t in terms.terms if any(t in kw for kw in self.frontmatter.kanon.keywords))


