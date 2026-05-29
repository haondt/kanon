from __future__ import annotations

from dataclasses import dataclass
from typing import override

from spek.core.config import SPEK_ADDRESS, SourceReference, SpekEnv
from spek.core.sources._local import LocalSource

@dataclass
class SpekSource(LocalSource):
    @classmethod
    def create(cls) -> SpekSource:
        root = SpekEnv.instance().repo_path
        return cls(original_address=SPEK_ADDRESS, root=root)

    @override
    def get_reference(self) -> SourceReference:
        return SourceReference.SPEK_SOURCE_REFERENCE
