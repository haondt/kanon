from __future__ import annotations

from kanon.core.ledger._blobs import LedgerBlobsMixin
from kanon.core.ledger._data import LEDGER_FILE, Progress
from kanon.core.ledger._json_target import JsonFileError, LedgerJsonMixin, check_json_file_readable
from kanon.core.ledger._persistence import LedgerFileError
from kanon.core.ledger._target import BACKUP_SUFFIX, TargetFileError

__all__ = [
    "BACKUP_SUFFIX",
    "LEDGER_FILE",
    "JsonFileError",
    "Ledger",
    "LedgerFileError",
    "Progress",
    "TargetFileError",
    "check_json_file_readable",
]


class Ledger(LedgerJsonMixin, LedgerBlobsMixin):
    """Rewindable record of what kanon wrote into user-owned target files and skill directories."""
