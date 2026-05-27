from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

import git

from spek.core.config import SOURCED_MODULES_DIR, SOURCED_PROFILES_DIR, SOURCED_REFS_DIR, SOURCED_STANCES_DIR, SourcedResource
from spek.core.sources._base import SourceResolver
from spek.core.sources._filesystem import FilesystemSource

LOCAL_SOURCE_TYPE_ID = "local"

@dataclass
class LocalSource(FilesystemSource):
    root: Path

    @property
    @override
    def specs_path(self) -> Path | None:
        return self.root / SOURCED_MODULES_DIR

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
    def serialize(self) -> str:
        return SourcedResource(LOCAL_SOURCE_TYPE_ID, str(self.root)).as_string

    @override
    def get_sha(self) -> str:
        try:
            repo = git.Repo(self.root)
            return repo.head.commit.hexsha
        except git.InvalidGitRepositoryError:
            return super().get_sha()

    @classmethod
    def parse(cls, resolver: SourceResolver, path: str) -> LocalSource:
        resolved = Path(path).expanduser().resolve()
        return LocalSource(_resolver=resolver, root=resolved)

