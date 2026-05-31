from __future__ import annotations

from dataclasses import dataclass
from typing import override

from kanon.core.config import KANON_ADDRESS, SourceReference, KanonEnv
from kanon.core.sources._local import LocalSource

@dataclass
class KanonSource(LocalSource):
    @classmethod
    def create(cls) -> KanonSource:
        root = KanonEnv.instance().repo_path
        return cls(original_address=KANON_ADDRESS, root=root)

    @override
    def get_reference(self) -> SourceReference:
        return SourceReference.KANON_SOURCE_REFERENCE
