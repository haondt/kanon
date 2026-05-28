from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from spek.core.config import SourceReference
from spek.core.modules import Module
from spek.core.profiles import ProfileSpec, ShallowProfile
from spek.core.references import NormalizedTerms, Reference
from spek.core.stances import Stance

@dataclass
class SourceResolver:
    get: Callable[[SourceReference], ParsedSource]
    try_get: Callable[[SourceReference], ParsedSource | None]
    def __getitem__(self, ref: SourceReference) -> ParsedSource:
        return self.get(ref)

@dataclass
class ParsedSource(ABC):
    _resolver: SourceResolver

    @abstractmethod
    def serialize(self) -> str:
        ...
    @abstractmethod
    def contains_module(self, path: str) -> bool:
        ...
    @abstractmethod
    def list_modules(self) -> list[str]:
        ...
    @abstractmethod
    def hydrate_module(self, path: str) -> Module:
        ...
    @abstractmethod
    def list_profiles(self) -> list[str]:
        ...
    @abstractmethod
    def _retrieve_profile_content(self, path: str) -> str:
        ...
    @abstractmethod
    def hydrate_profile(self, path: str) -> ProfileSpec:
        ...
    @abstractmethod
    def shallow_hydrate_profile(self, path: str) -> ShallowProfile:
        ...
    @abstractmethod
    def search_references(self, terms: list[str] | NormalizedTerms, limit: int = 0, match_all: bool = True) -> list[Reference]:
        ...
    @abstractmethod
    def hydrate_reference(self, path: str) -> Reference:
        ...
    @abstractmethod
    def contains_stance(self, path: str) -> bool:
        ...
    @abstractmethod
    def list_stances(self) -> list[str]:
        ...
    @abstractmethod
    def hydrate_stance(self, path: str) -> Stance:
        ...
    @abstractmethod
    def get_sha(self) -> str:
        ...
