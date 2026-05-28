from __future__ import annotations

from dataclasses import dataclass

from spek.core.config import ALIAS_SCHEME, SourceReference
from spek.core.sources._base import ParsedSource

@dataclass
class AliasRef:
    name: str

    def resolve(self, merged: dict[SourceReference, ParsedSource | AliasRef], chain: list[SourceReference]) -> ParsedSource:
        """Resolve all AliasRef values, detecting cycles."""
        next = SourceReference(ALIAS_SCHEME, self.name)
        if next in chain:
            cycle = " → ".join([i.as_string for i in chain + [next]])
            raise ValueError(f"Cycle detected in sources: {cycle}")

        if not (next_source := merged.get(next)):
            raise ValueError(f"Could not resolve alias {next.as_string}")

        if isinstance(next_source, AliasRef):
            return next_source.resolve(merged, chain + [next])
        return next_source
