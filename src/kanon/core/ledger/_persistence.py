from __future__ import annotations

import json
from pathlib import Path
from typing import Self

from pydantic import ValidationError

from kanon.commands._utils import kanon_command
from kanon.core.errors import KanonRuntimeError
from kanon.core.ledger._data import LedgerData


class LedgerFileError(KanonRuntimeError):
    pass


class LedgerPersistenceMixin(LedgerData):
    @classmethod
    def load(cls, path: Path) -> Self:
        """Load the ledger at `path`; a missing file is an empty ledger."""
        if not path.exists():
            return cls(path=path)
        try:
            return cls.model_validate({**json.loads(path.read_text()), "path": path})
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            raise LedgerFileError(
                f"{path} is not a valid ledger (written by an older kanon?); delete it and run {kanon_command("sync")} again"
            ) from e

    def save(self) -> None:
        """Write the ledger; an empty ledger removes the file."""
        for name in list(self.integrations):
            self.prune(name)
        if not self.integrations:
            self.path.unlink(missing_ok=True)
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.model_dump(mode="json", exclude_none=True), indent=2) + "\n")
