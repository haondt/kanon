from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Callable, override, Any

from pydantic import BaseModel, Field

from spek.core.config import SourcedResource
from spek.core.yaml_utils import parse_yaml

class ShallowProfile(BaseModel):
    description: str = Field(default_factory=str)
    extends: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    stances: list[str] = Field(default_factory=list)

    @override
    def model_post_init(self, context: Any, /) -> None:
        self.modules = SourcedResource.sanitize(self.modules)
        self.stances = SourcedResource.sanitize(self.stances)
        self.extends = SourcedResource.sanitize(self.extends)
        return super().model_post_init(context)
    @classmethod
    def load(cls,  content: str) -> ShallowProfile:
        data = parse_yaml(content)
        return ShallowProfile.model_validate(data)

@dataclass
class ProfileSpec:
    description: str
    modules_set: set[str]
    stances_set: set[str]

    @cached_property
    def modules(self) -> list[str]:
        return SourcedResource.sanitize(self.modules_set)
    @cached_property
    def stances(self) -> list[str]:
        return SourcedResource.sanitize(self.stances_set)


    @classmethod
    def load(cls,  content: str, content_factory: Callable[[str], str],  seen: frozenset[str]) -> ProfileSpec:
        spec = ShallowProfile.load(content)
        final_spec = ProfileSpec(
            description=spec.description,
            modules_set=set(spec.modules),
            stances_set=set(spec.stances)
        )

        for parent_ref in spec.extends:
            if parent_ref in seen:
                raise ValueError(f"Circular profile dependency: {parent_ref}")
            parent_content = content_factory(parent_ref)
            parent = ProfileSpec.load(parent_content, content_factory, seen | {parent_ref})
            final_spec.modules_set = final_spec.modules_set | parent.modules_set
            final_spec.stances_set = final_spec.stances_set | parent.stances_set

        return final_spec
