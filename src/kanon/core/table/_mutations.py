from __future__ import annotations

from kanon.core.errors import KanonValueError
from kanon.core.table._keys import edge_pair, key_for
from kanon.core.table._models import TableData, TableEdge, TableItem, TableStatus


class TableMutationsMixin(TableData):
    def add(self, title: str, summary: str = "", links: list[str] | None = None) -> tuple[str, bool]:
        """Add an open item; return (key, created). An existing title (case-insensitive) is a no-op."""
        title = title.strip()
        if not title:
            raise KanonValueError("Title must not be empty.")
        for key, item in self.items.items():
            if item.title.lower() == title.lower():
                return key, False
        for target in links or []:
            self.get_or_raise(target)
        key = key_for(self.next_index)
        self.next_index += 1
        self.items[key] = TableItem(title=title, summary=summary.strip())
        for target in links or []:
            self.link_items(key, target)
        return key, True

    def edit_item(self, key: str, title: str | None = None, summary: str | None = None) -> None:
        item = self.get_or_raise(key)
        if title is not None:
            if not title.strip():
                raise KanonValueError("Title must not be empty.")
            item.title = title.strip()
        if summary is not None:
            item.summary = summary.strip()

    def set_status(self, key: str, status: TableStatus) -> str | None:
        """Set an item's status; return the key of the item demoted from active, if any."""
        item = self.get_or_raise(key)
        demoted = None
        if status == "active":
            for other_key, other in self.items.items():
                if other_key != key and other.status == "active":
                    other.status = "open"
                    demoted = other_key
        item.status = status
        return demoted

    def link_items(self, a: str, b: str) -> bool:
        """Add an undirected edge; return False if it already existed."""
        if a == b:
            raise KanonValueError("Cannot link an item to itself.")
        self.get_or_raise(a)
        self.get_or_raise(b)
        if self.has_edge(a, b):
            return False
        low, high = edge_pair(a, b)
        self.edges.append(TableEdge(a=low, b=high))
        return True

    def unlink_items(self, a: str, b: str) -> None:
        self.get_or_raise(a)
        self.get_or_raise(b)
        if not self.has_edge(a, b):
            raise KanonValueError(f"{a!r} and {b!r} are not linked.")
        pair = edge_pair(a, b)
        self.edges = [e for e in self.edges if edge_pair(e.a, e.b) != pair]

    def remove_item(self, key: str) -> None:
        self.get_or_raise(key)
        del self.items[key]
        self.edges = [e for e in self.edges if key not in (e.a, e.b)]

    def merge_items(self, keep: str, absorb: str) -> None:
        """Fold `absorb` into `keep`. Active wins; resolved only if both are resolved."""
        if keep == absorb:
            raise KanonValueError("Cannot merge an item into itself.")
        kept, gone = self.get_or_raise(keep), self.get_or_raise(absorb)
        if "active" in (kept.status, gone.status):
            kept.status = "active"
        elif kept.status == gone.status == "resolved":
            kept.status = "resolved"
        else:
            kept.status = "open"
        kept.summary = "\n\n".join(s for s in (kept.summary, gone.summary) if s)
        absorbed_neighbors = self.neighbors(absorb)
        self.remove_item(absorb)
        for other in absorbed_neighbors:
            if other != keep:
                self.link_items(keep, other)
