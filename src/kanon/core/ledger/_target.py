from __future__ import annotations

import shutil
from pathlib import Path

from kanon.core.errors import KanonRuntimeError

BACKUP_SUFFIX = ".kanon-bak"


class TargetFileError(KanonRuntimeError):
    pass


def backup_target(target: Path) -> None:
    """Copy `target` to `<target>.kanon-bak` the first time kanon touches it."""
    backup = target.with_name(target.name + BACKUP_SUFFIX)
    if target.exists() and not backup.exists():
        shutil.copy2(target, backup)
