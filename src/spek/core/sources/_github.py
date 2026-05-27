from __future__ import annotations

from dataclasses import dataclass
from typing import override

from spek.core.config import SourcedResource
from spek.core.modules import Module
from spek.core.profiles import ProfileSpec, ShallowProfile
from spek.core.references import NormalizedTerms, Reference
from spek.core.stances import Stance
from spek.core.sources._base import ParsedSource, SourceResolver

GITHUB_SOURCE_TYPE_ID = "gh"

@dataclass
class GitHubSource(ParsedSource):
    org: str
    repo: str
    ref: str | None

    @classmethod
    def parse(cls, resolver: SourceResolver, path: str) -> GitHubSource:
        rest, _, ref = path.partition("@")
        ref = ref or None
        parts = rest.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError(f"Invalid GitHub source path: {path!r}. Expected gh::org/repo[@ref]")
        return GitHubSource(_resolver=resolver, org=parts[0], repo=parts[1], ref=ref)

    @override
    def serialize(self) -> str:
        path = f'{self.org}/{self.repo}'
        if self.ref:
            path = f'{path}@{self.ref}'
        return SourcedResource(GITHUB_SOURCE_TYPE_ID, path).as_string

    @override
    def contains_module(self, path: str) -> bool:
        return False # todo
    @override
    def list_modules(self) -> list[str]:
        return [] # todo
    @override
    def hydrate_module(self, path: str) -> Module:
        raise NotImplementedError() # todo
    @override
    def list_profiles(self) -> list[str]:
        return [] # todo
    @override
    def _retrieve_profile_content(self, path: str) -> str:
        raise NotImplementedError() # todo
    @override
    def hydrate_profile(self, path: str) -> ProfileSpec:
        raise NotImplementedError() # todo
    @override
    def shallow_hydrate_profile(self, path: str) -> ShallowProfile:
        raise NotImplementedError() # todo
    @override
    def search_references(self, terms: list[str] | NormalizedTerms, limit: int = 0, match_all: bool = True) -> list[Reference]:
        return [] # todo
    @override
    def hydrate_reference(self, path: str) -> Reference:
        raise NotImplementedError() # todo
    @override
    def list_stances(self) -> list[str]:
        return [] # todo
    @override
    def hydrate_stance(self, path: str) -> Stance:
        raise NotImplementedError() # todo
    @override
    def get_sha(self) -> str:
        raise NotImplementedError() # todo
