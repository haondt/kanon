from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Callable, override, Any

from pydantic import BaseModel, Field

from spek.core.config import SourceReference, SourcedResource
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
    modules_set: set[SourcedResource]
    stances_set: set[SourcedResource]

    @cached_property
    def modules(self) -> list[str]:
        return [i.as_string for i in sorted(self.modules_set, key=lambda r: r.as_fully_qualified_string)]
    @cached_property
    def stances(self) -> list[str]:
        return [i.as_string for i in sorted(self.stances_set, key=lambda r: r.as_fully_qualified_string)]

    @classmethod
    def load(cls,  content: str, content_factory: Callable[[SourcedResource], str], self_reference: SourceReference,  seen: frozenset[SourcedResource]) -> ProfileSpec:
        spec = ShallowProfile.load(content)
        modules_set: set[SourcedResource] = set()
        for module_ref in spec.modules:
            module_res: SourcedResource = SourcedResource.parse(module_ref)
            if module_res.source == SourceReference.SELF_SOURCE_REFERENCE:
                module_res = SourcedResource(self_reference, module_res.path)
            modules_set.add(module_res)
        stances_set: set[SourcedResource] = set()
        for stance_ref in spec.stances:
            stance_res: SourcedResource = SourcedResource.parse(stance_ref)
            if stance_res.source == SourceReference.SELF_SOURCE_REFERENCE:
                stance_res = SourcedResource(self_reference, stance_res.path)
            stances_set.add(stance_res)
        final_spec = ProfileSpec(
            description=spec.description,
            modules_set=modules_set,
            stances_set=stances_set,
        )

        for parent_ref in [SourcedResource.parse(r) for r in spec.extends]:
            if parent_ref.source == SourceReference.SELF_SOURCE_REFERENCE:
                parent_ref = SourcedResource(self_reference, parent_ref.path)
            if parent_ref in seen:
                raise ValueError(f"Circular profile dependency: {parent_ref}")
            parent_content = content_factory(parent_ref)
            parent = ProfileSpec.load(parent_content, content_factory, parent_ref.source, seen | {parent_ref})
            final_spec.modules_set = final_spec.modules_set | parent.modules_set
            final_spec.stances_set = final_spec.stances_set | parent.stances_set

        return final_spec
