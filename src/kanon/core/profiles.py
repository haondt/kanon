from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Callable, override, Any

from pydantic import BaseModel, Field

from kanon.core.config import SourceReference, SourcedResource
from kanon.core.yaml_utils import parse_yaml

class ShallowProfile(BaseModel):
    description: str = Field(default_factory=str)
    extends: list[str] = Field(default_factory=list)
    kanons: list[str] = Field(default_factory=list)
    stances: list[str] = Field(default_factory=list)

    @override
    def model_post_init(self, context: Any, /) -> None:
        self.kanons = SourcedResource.sanitize(self.kanons)
        self.stances = SourcedResource.sanitize(self.stances)
        self.extends = SourcedResource.sanitize(self.extends)
        return super().model_post_init(context)
    @classmethod
    def load(cls,  content: str) -> ShallowProfile:
        data = parse_yaml(content)
        return ShallowProfile.model_validate(data)

@dataclass
class Profile:
    description: str
    kanons_set: set[SourcedResource]
    stances_set: set[SourcedResource]

    @cached_property
    def kanons(self) -> list[str]:
        return [i.as_string for i in sorted(self.kanons_set, key=lambda r: r.as_fully_qualified_string)]
    @cached_property
    def stances(self) -> list[str]:
        return [i.as_string for i in sorted(self.stances_set, key=lambda r: r.as_fully_qualified_string)]

    @classmethod
    def load(cls,  content: str, content_factory: Callable[[SourcedResource], str], self_reference: SourceReference,  seen: frozenset[SourcedResource]) -> Profile:
        profile = ShallowProfile.load(content)
        kanons_set: set[SourcedResource] = set()
        for kanon_ref in profile.kanons:
            kanon_res: SourcedResource = SourcedResource.parse(kanon_ref)
            if kanon_res.source == SourceReference.SELF_SOURCE_REFERENCE:
                kanon_res = SourcedResource(self_reference, kanon_res.path, kanon_res.args)
            kanons_set.add(kanon_res)
        stances_set: set[SourcedResource] = set()
        for stance_ref in profile.stances:
            stance_res: SourcedResource = SourcedResource.parse(stance_ref)
            if stance_res.source == SourceReference.SELF_SOURCE_REFERENCE:
                stance_res = SourcedResource(self_reference, stance_res.path, stance_res.args)
            stances_set.add(stance_res)
        final_profile = Profile(
            description=profile.description,
            kanons_set=kanons_set,
            stances_set=stances_set,
        )

        for parent_ref in [SourcedResource.parse(r) for r in profile.extends]:
            if parent_ref.source == SourceReference.SELF_SOURCE_REFERENCE:
                parent_ref = SourcedResource(self_reference, parent_ref.path, parent_ref.args)
            if parent_ref in seen:
                raise ValueError(f"Circular profile dependency: {parent_ref}")
            parent_content = content_factory(parent_ref)
            parent = Profile.load(parent_content, content_factory, parent_ref.source, seen | {parent_ref})
            final_profile.kanons_set = final_profile.kanons_set | parent.kanons_set
            final_profile.stances_set = final_profile.stances_set | parent.stances_set

        return final_profile
