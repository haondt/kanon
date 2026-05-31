from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

import git

from kanon.core.config import LOCAL_SCHEME, SOURCED_KANONS_DIR, SOURCED_PROFILES_DIR, SOURCED_REFS_DIR, SOURCED_STANCES_DIR, SourceReference
from kanon.core.sources._filesystem import FilesystemSource

@dataclass
class LocalSource(FilesystemSource):
    original_address: str
    root: Path

    @property
    @override
    def kanons_path(self) -> Path | None:
        return self.root / SOURCED_KANONS_DIR

    @property
    @override
    def profiles_path(self) -> Path | None:
        return self.root / SOURCED_PROFILES_DIR

    @property
    @override
    def references_path(self) -> Path | None:
        return self.root / SOURCED_REFS_DIR

    @property
    @override
    def stances_path(self) -> Path | None:
        return self.root / SOURCED_STANCES_DIR

    @override
    def get_reference(self) -> SourceReference:
        return SourceReference(LOCAL_SCHEME, self.original_address)

    @override
    def get_sha(self) -> str:
        try:
            repo = git.Repo(self.root)
            return repo.head.commit.hexsha
        except git.InvalidGitRepositoryError:
            return super().get_sha()

    @classmethod
    def parse(cls, address: str) -> LocalSource:
        resolved = Path(address).expanduser().resolve()
        return LocalSource(original_address=address, root=resolved)

