from __future__ import annotations

import hashlib
from abc import abstractmethod, ABC
from dataclasses import dataclass
from pathlib import Path
from typing import override

from kanon.core.config import SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.profiles import Profile, ShallowProfile
from kanon.core.references import NormalizedTerms, Reference
from kanon.core.stances import Stance
from kanon.core.sources._base import ParsedSource, SourceResolver


@dataclass
class FilesystemSource(ParsedSource, ABC):
    @property
    @abstractmethod
    def kanons_path(self) -> Path | None:
        ...

    @property
    @abstractmethod
    def profiles_path(self) -> Path | None:
        ...

    @property
    @abstractmethod
    def references_path(self) -> Path | None:
        ...

    @property
    @abstractmethod
    def stances_path(self) -> Path | None:
        ...

    @override
    def contains_kanon(self, path: str) -> bool:
        if self.kanons_path is None:
            return False
        return (self.kanons_path / path).with_suffix(".md").is_file()

    @override
    def list_kanons(self) -> list[str]:
        if self.kanons_path is None or not self.kanons_path.exists():
            return []
        kanons: list[str] = []
        for src in sorted(self.kanons_path.rglob("*.md")):
            rel = str(src.relative_to(self.kanons_path).with_suffix(""))
            kanons.append(rel)
        return sorted(kanons)

    @override
    def hydrate_kanon(self, path: str) -> Kanon:
        assert self.kanons_path is not None
        file_path = self.kanons_path.joinpath(*path.split("/")).with_suffix(".md")
        return Kanon.load(file_path.read_text())

    @override
    def list_profiles(self) -> list[str]:
        if self.profiles_path is None or not self.profiles_path.exists():
            return []
        profiles: list[str] = []
        for src in sorted(self.profiles_path.rglob("*.yaml")):
            rel = str(src.relative_to(self.profiles_path).with_suffix(""))
            profiles.append(rel)
        return sorted(profiles)

    @override
    def _retrieve_profile_content(self, path: str) -> str:
        assert self.profiles_path is not None
        file_path = self.profiles_path.joinpath(*path.split("/")).with_suffix(".yaml")
        return file_path.read_text()

    @override
    def hydrate_profile(self, ref: SourcedResource) -> Profile:
        def _retrieve_profile_content_from_ref(parsed_ref: SourcedResource) -> str:
            source = SourceResolver.instance()[parsed_ref.source]
            return source._retrieve_profile_content(parsed_ref.path)
        profile_content = self._retrieve_profile_content(ref.path)
        self_reference = SourcedResource(self.get_reference(), path=ref.path, args=ref.args)
        return Profile.load(profile_content, _retrieve_profile_content_from_ref, ref.source, frozenset({self_reference}))

    @override
    def shallow_hydrate_profile(self, path: str) -> ShallowProfile:
        profile_content = self._retrieve_profile_content(path)
        return ShallowProfile.load(profile_content)

    @override
    def search_references(self, terms: list[str] | NormalizedTerms, limit: int = 0, match_all: bool = True) -> list[Reference]:
        if self.references_path is None or not self.references_path.exists():
            return []
        if isinstance(terms, list):
            terms = NormalizedTerms(terms)
        scored: list[tuple[int, Reference]] = []
        for src in sorted(self.references_path.rglob("*.md")):
            path = str(src.relative_to(self.references_path).with_suffix(""))
            ref = Reference.load(path, src.read_text())
            score = ref.score(terms)
            if match_all and score < len(terms):
                continue
            if not match_all and score == 0:
                continue
            scored.append((score, ref))
        scored.sort(key=lambda x: x[0], reverse=True)
        scored = scored[:limit] if limit > 0 else scored
        return [r for _, r in scored]

    @override
    def hydrate_reference(self, path: str) -> Reference:
        assert self.references_path is not None
        file_path = self.references_path.joinpath(*path.split("/")).with_suffix(".md")
        reference_content = file_path.read_text()
        return Reference.load(path, reference_content)

    @override
    def contains_stance(self, path: str) -> bool:
        if self.stances_path is None:
            return False
        return (self.stances_path / path).with_suffix(".yaml").is_file()

    @override
    def list_stances(self) -> list[str]:
        if self.stances_path is None or not self.stances_path.exists():
            return []
        return sorted(
            str(src.relative_to(self.stances_path).with_suffix(""))
            for src in sorted(self.stances_path.rglob("*.yaml"))
        )

    @override
    def hydrate_stance(self, path: str) -> Stance:
        assert self.stances_path is not None
        file_path = self.stances_path.joinpath(*path.split("/")).with_suffix(".yaml")
        return Stance.load(file_path.read_text())

    @override
    def get_sha(self) -> str:
        h = hashlib.sha256()
        seen: set[Path] = set()
        for base in [self.kanons_path, self.profiles_path, self.references_path, self.stances_path]:
            if base is None or not base.exists() or base in seen:
                continue
            seen.add(base)
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    h.update(str(path.relative_to(base)).encode())
                    h.update(path.read_bytes())
        return h.hexdigest()[:40]

