from __future__ import annotations

from dataclasses import dataclass
from typing import override

from spek.core.config import SPEK_ADDRESS, SourceReference, SpekEnv
from spek.core.sources._base import SourceResolver
from spek.core.sources._local import LocalSource

@dataclass
class SpekSource(LocalSource):
    @classmethod
    def create(cls, resolver: SourceResolver) -> SpekSource:
        root = SpekEnv.instance().repo_path
        return cls(_resolver=resolver, original_address=SPEK_ADDRESS, root=root)

    @override
    def serialize(self) -> str:
        return SourceReference.SPEK_SOURCE_REFERENCE.as_string
