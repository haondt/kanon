from __future__ import annotations

from dataclasses import dataclass, field
from typing import override

from spek.core.config import SourceReference
from spek.core.modules import Module
from spek.core.profiles import ProfileSpec, ShallowProfile
from spek.core.references import NormalizedTerms, Reference
from spek.core.stances import Stance
from spek.core.sources._base import ParsedSource


@dataclass
class SelfSource(ParsedSource):
    parent: ParsedSource | None = field(default=None, compare=False)

    def _require_parent(self) -> ParsedSource:
        if self.parent is None:
            raise ValueError(
                "spek::self has no source context — only valid inside a profile"
            )
        return self.parent

    @override
    def serialize(self) -> str:
        return SourceReference.SELF_SOURCE_REFERENCE.as_string

    @override
    def contains_module(self, path: str) -> bool:
        if self.parent is None:
            return False
        return self.parent.contains_module(path)

    @override
    def list_modules(self) -> list[str]:
        if self.parent is None:
            return []
        return self.parent.list_modules()

    @override
    def hydrate_module(self, path: str) -> Module:
        return self._require_parent().hydrate_module(path)

    @override
    def list_profiles(self) -> list[str]:
        if self.parent is None:
            return []
        return self.parent.list_profiles()

    @override
    def _retrieve_profile_content(self, path: str) -> str:
        return self._require_parent()._retrieve_profile_content(path)

    @override
    def hydrate_profile(self, path: str) -> ProfileSpec:
        return self._require_parent().hydrate_profile(path)

    @override
    def shallow_hydrate_profile(self, path: str) -> ShallowProfile:
        return self._require_parent().shallow_hydrate_profile(path)

    @override
    def search_references(self, terms: list[str] | NormalizedTerms, limit: int = 0, match_all: bool = True) -> list[Reference]:
        if self.parent is None:
            return []
        return self.parent.search_references(terms, limit, match_all)

    @override
    def hydrate_reference(self, path: str) -> Reference:
        return self._require_parent().hydrate_reference(path)

    @override
    def contains_stance(self, path: str) -> bool:
        if self.parent is None:
            return False
        return self.parent.contains_stance(path)

    @override
    def list_stances(self) -> list[str]:
        if self.parent is None:
            return []
        return self.parent.list_stances()

    @override
    def hydrate_stance(self, path: str) -> Stance:
        return self._require_parent().hydrate_stance(path)

    @override
    def get_sha(self) -> str:
        return self._require_parent().get_sha()
