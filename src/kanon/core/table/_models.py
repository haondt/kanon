from __future__ import annotations

from typing import Literal, NoReturn

from pydantic import BaseModel, Field

from kanon.core.errors import KanonKeyError
from kanon.core.table._keys import edge_pair, key_order

TableStatus = Literal["open", "active", "resolved"]


class TableItem(BaseModel):
    title: str
    summary: str = ""
    status: TableStatus = "open"


class TableEdge(BaseModel):
    a: str
    b: str


class TableData(BaseModel):
    """Fields and read-only accessors shared by the TableState mixins."""

    next_index: int = 0
    items: dict[str, TableItem] = Field(default_factory=dict)
    edges: list[TableEdge] = Field(default_factory=list)

    def get(self, key: str) -> TableItem | None:
        return self.items.get(key)

    def get_or_raise(self, key: str) -> TableItem:
        item = self.get(key)
        if item is None:
            self._raise_key_error(key)
        return item

    def _raise_key_error(self, key: str) -> NoReturn:
        valid = ", ".join(sorted(self.items, key=key_order)) or "none"
        raise KanonKeyError(f"No item {key!r}. Valid keys: {valid}")

    def has_edge(self, a: str, b: str) -> bool:
        pair = edge_pair(a, b)
        return any(edge_pair(e.a, e.b) == pair for e in self.edges)

    def neighbors(self, key: str) -> list[str]:
        found = {e.b if e.a == key else e.a for e in self.edges if key in (e.a, e.b)}
        return sorted(found, key=key_order)
