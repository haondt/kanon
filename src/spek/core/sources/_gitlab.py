from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

import git

from spek.core.config import (
    GITLAB_SCHEME,
    SOURCED_MODULES_DIR,
    SOURCED_PROFILES_DIR,
    SOURCED_REFS_DIR,
    SOURCED_STANCES_DIR,
    SpekEnv,
    SourceReference,
)
from spek.core.sources._base import PullResult, SourceResolver
from spek.core.sources._filesystem import FilesystemSource


@dataclass
class GitLabSource(FilesystemSource):
    groups: list[str]
    repo: str
    ref: str | None

    @classmethod
    def parse(cls, resolver: SourceResolver, address: str) -> GitLabSource:
        rest, _, ref = address.partition("@")
        ref = ref or None
        parts = rest.split("/")
        if len(parts) < 2 or not all(parts):
            raise ValueError(
                f"Invalid GitLab source path: {address!r}. Expected gl::group/.../repo[@ref]"
            )
        return GitLabSource(_resolver=resolver, groups=parts[:-1], repo=parts[-1], ref=ref)

    @override
    def serialize(self) -> str:
        path = '/'.join(self.groups + [self.repo])
        if self.ref:
            path = f'{path}@{self.ref}'
        return SourceReference(GITLAB_SCHEME, path).as_string

    @override
    def cache_path(self) -> Path:
        base = SpekEnv.instance().sources_cache_path / GITLAB_SCHEME / '/'.join(self.groups + [self.repo])
        if self.ref:
            return Path(f"{base}@{self.ref}")
        return base

    def _ensure_cloned(self) -> Path:
        path = self.cache_path()
        if not (path / ".git").exists():
            url = f"https://gitlab.com/{'/'.join(self.groups)}/{self.repo}.git"
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
