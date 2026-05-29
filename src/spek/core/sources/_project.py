from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

from spek.core.config import PROJECT_MODULES_DIR, PROJECT_PROFILES_DIR, PROJECT_REFS_DIR, PROJECT_STANCES_DIR, SourceReference, SpekConfig
from spek.core.sources._filesystem import FilesystemSource

@dataclass
class ProjectSource(FilesystemSource):

    @property
    @override
    def specs_path(self) -> Path | None:
        return SpekConfig.root() / PROJECT_MODULES_DIR

    @property
    @override
    def profiles_path(self) -> Path | None:
        return SpekConfig.root() / PROJECT_PROFILES_DIR

    @property
    @override
    def references_path(self) -> Path | None:
        return SpekConfig.root() / PROJECT_REFS_DIR

    @property
    @override
    def stances_path(self) -> Path | None:
        return SpekConfig.root() / PROJECT_STANCES_DIR

    @override
    def get_reference(self) -> SourceReference:
        return SourceReference.PROJECT_SOURCE_REFERENCE
