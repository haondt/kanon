from __future__ import annotations

from kanon.core.table._keys import key_for, key_order
from kanon.core.table._lint import TableLintMixin
from kanon.core.table._models import TableEdge, TableItem, TableStatus
from kanon.core.table._mutations import TableMutationsMixin
from kanon.core.table._persistence import TablePersistenceMixin
from kanon.core.table._render import TableRenderMixin, status_label

__all__ = [
    "TableEdge",
    "TableItem",
    "TableState",
    "TableStatus",
    "key_for",
    "key_order",
    "status_label",
]


class TableState(TablePersistenceMixin, TableMutationsMixin, TableRenderMixin, TableLintMixin):
    pass
