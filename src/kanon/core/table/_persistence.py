from __future__ import annotations

from typing import Self

from kanon.core.config import TABLE_FILE, KanonConfig
from kanon.core.table._models import TableData
from kanon.core.utils import hash_text
from kanon.core.yaml_utils import dump_yaml, parse_yaml


class TablePersistenceMixin(TableData):
    @classmethod
    def load(cls) -> tuple[Self, str]:
        """Load table.yaml; return (state, file_hash). A missing file is an empty table with an empty hash."""
        path = KanonConfig.root() / TABLE_FILE
        if not path.exists():
            return cls(), ""
        text = path.read_text()
        return cls.model_validate(parse_yaml(text)), hash_text(text)

    def save(self) -> tuple[str, str]:
        """Save table.yaml; return (before_hash, after_hash)."""
        path = KanonConfig.root() / TABLE_FILE
        before = hash_text(path.read_text() if path.exists() else "")
        text = dump_yaml(self)
        path.write_text(text)
        return before, hash_text(text)

    @staticmethod
    def clear() -> bool:
        """Delete table.yaml; return whether it existed."""
        path = KanonConfig.root() / TABLE_FILE
        existed = path.exists()
        path.unlink(missing_ok=True)
        return existed
