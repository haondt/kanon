from __future__ import annotations

from pathlib import Path

from kanon.core.config import Integration
from kanon.core.ledger._data import Progress
from kanon.core.ledger._models import BlobEntry, BlobKind
from kanon.core.ledger._persistence import LedgerPersistenceMixin


class LedgerBlobsMixin(LedgerPersistenceMixin):
    def claim_blob(self, integration: str, path: Path, kind: BlobKind, on_progress: Progress = None) -> None:
        """Record that kanon owns `path` wholesale."""
        self.integration_ledger(integration).blobs[str(path)] = BlobEntry(kind=kind)
        self.save()
        if on_progress:
            on_progress(f"  ledger: {integration} {kind} {path}")

    def has_blob(self, integration: Integration, path: Path) -> bool:
        recorded = self.integrations.get(integration)
        return recorded is not None and str(path) in recorded.blobs

    def owned_blobs(self, integration: Integration, kind: BlobKind | None = None) -> list[Path]:
        recorded = self.integrations.get(integration)
        blobs = recorded.blobs if recorded else {}
        return sorted(Path(k) for k, v in blobs.items() if kind is None or v.kind == kind)

    def release_blobs(self, integration: Integration, kind: BlobKind | None = None) -> None:
        """Forget the blobs recorded for `integration` (after they were removed)."""
        recorded = self.integrations.get(integration)
        if recorded:
            for path in self.owned_blobs(integration, kind):
                del recorded.blobs[str(path)]
        self.prune(integration)
        self.save()
