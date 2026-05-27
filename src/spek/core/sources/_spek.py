from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import override

from spek.core.config import SPEK_SOURCE, SourcedResource
from spek.core.sources._local import LocalSource

@dataclass
class SpekSource(LocalSource):
    @override
    def serialize(self) -> str:
        return SourcedResource(SPEK_SOURCE, SPEK_SOURCE).as_string
