from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, TypeVar
from collections.abc import Iterable

from kanon.core.config import SourceReference, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.profiles import Profile, ShallowProfile
from kanon.core.references import NormalizedTerms, Reference
from kanon.core.stances import Stance

T = TypeVar("T", SourceReference, SourcedResource)


class PullResult(StrEnum):
    CLONED = "cloned"
    PULLED = "pulled"
    CACHED = "cached"
    NOOP = "noop"


class SourceResolver(ABC):
    _instance: ClassVar[SourceResolver | None] = None

    @classmethod
    def initialize(cls, instance: SourceResolver):
        cls._instance = instance

    @classmethod
    def instance(cls) -> SourceResolver:
        if cls._instance is None:
            raise RuntimeError("SourceResolver has not been initialized. Call SourceResolver.initialize() first.")
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @abstractmethod
    def resolve(self, ref: SourceReference) -> ParsedSource:
        ...

    @abstractmethod
    def dealias(self, ref: T) -> T:
        ...

    @abstractmethod
    def try_resolve(self, ref: SourceReference) -> ParsedSource | None:
        ...

    @abstractmethod
    def items(self) -> Iterable[tuple[SourceReference, ParsedSource]]:
        ...

    @abstractmethod
    def __getitem__(self, ref: SourceReference) -> ParsedSource:
        ...

@dataclass
class ParsedSource(ABC):
    @abstractmethod
    def get_reference(self) -> SourceReference:
        ...
    def serialize(self) -> str:
        return self.get_reference().as_string
    @abstractmethod
    def contains_kanon(self, path: str) -> bool:
        ...
    @abstractmethod
    def list_kanons(self) -> list[str]:
        ...
    @abstractmethod
    def hydrate_kanon(self, path: str) -> Kanon:
        ...
    @abstractmethod
    def list_profiles(self) -> list[str]:
        ...
    @abstractmethod
    def _retrieve_profile_content(self, path: str) -> str:
        ...
    @abstractmethod
    def hydrate_profile(self, ref: SourcedResource) -> Profile:
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

    def pull(self, force: bool = False) -> PullResult: # pyright: ignore[reportUnusedParameter]
        return PullResult.NOOP

    def cache_path(self) -> Path | None:
        return None
