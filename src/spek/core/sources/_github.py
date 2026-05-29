from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

import git

from spek.core.config import (
    GITHUB_SCHEME,
    SOURCED_MODULES_DIR,
    SOURCED_PROFILES_DIR,
    SOURCED_REFS_DIR,
    SOURCED_STANCES_DIR,
    SourceReference,
)
from spek.core.sources._base import PullResult
from spek.core.sources._filesystem import FilesystemSource


@dataclass
class GitHubSource(FilesystemSource):
    org: str
    repo: str
    ref: str | None


    @override
    def cache_path(self) -> Path:
        return self.get_reference().cache_path()

    @classmethod
    def parse(cls, address: str) -> GitHubSource:
        rest, _, ref = address.partition("@")
        ref = ref or None
        parts = rest.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError(f"Invalid GitHub source path: {address!r}. Expected gh::org/repo[@ref]")
        return GitHubSource(org=parts[0], repo=parts[1], ref=ref)

    @override
    def get_reference(self) -> SourceReference:
        path = f'{self.org}/{self.repo}'
        if self.ref:
            path = f'{path}@{self.ref}'
        return SourceReference(GITHUB_SCHEME, path)


    def _ensure_cloned(self) -> Path:
        path = self.cache_path()
        if not (path / ".git").exists():
            url = f"https://github.com/{self.org}/{self.repo}.git"
            repo = git.Repo.clone_from(url, str(path))
            if self.ref:
                repo.git.checkout(self.ref)
        return path

    @override
    def pull(self, force: bool = False) -> PullResult:
        path = self.cache_path()
        already_existed = (path / ".git").exists()
        self._ensure_cloned()
        if not already_existed:
            return PullResult.CLONED
        if force:
            repo = git.Repo(str(path))
            repo.remotes.origin.pull()
            return PullResult.PULLED
        return PullResult.CACHED

    @property
    @override
    def specs_path(self) -> Path | None:
        path = self._ensure_cloned() / SOURCED_MODULES_DIR
        return path if path.exists() else None

    @property
    @override
    def profiles_path(self) -> Path | None:
        path = self._ensure_cloned() / SOURCED_PROFILES_DIR
        return path if path.exists() else None

    @property
    @override
    def references_path(self) -> Path | None:
        path = self._ensure_cloned() / SOURCED_REFS_DIR
        return path if path.exists() else None

    @property
    @override
    def stances_path(self) -> Path | None:
        path = self._ensure_cloned() / SOURCED_STANCES_DIR
        return path if path.exists() else None

    @override
    def get_sha(self) -> str:
        repo = git.Repo(str(self._ensure_cloned()))
        return repo.head.commit.hexsha
