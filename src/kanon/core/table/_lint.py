from __future__ import annotations

from kanon.core.table._keys import edge_pair
from kanon.core.table._models import TableData


class TableLintMixin(TableData):
    def lint(self) -> list[str]:
        issues: list[str] = []
        active = [k for k, i in self.items.items() if i.status == "active"]
        if len(active) > 1:
            issues.append(f"multiple active items: {', '.join(active)}")
        seen_titles: dict[str, str] = {}
        for key, item in self.items.items():
            if not item.title.strip():
                issues.append(f"item {key!r} has empty title")
            lowered = item.title.lower()
            if lowered in seen_titles:
                issues.append(f"items {seen_titles[lowered]!r} and {key!r} share a title")
            seen_titles[lowered] = key
        seen_edges: set[tuple[str, str]] = set()
        for e in self.edges:
            for end in (e.a, e.b):
                if end not in self.items:
                    issues.append(f"edge {e.a}-{e.b} references missing item {end!r}")
            if e.a == e.b:
                issues.append(f"edge {e.a}-{e.b} links an item to itself")
            pair = edge_pair(e.a, e.b)
            if pair in seen_edges:
                issues.append(f"duplicate edge {pair[0]}-{pair[1]}")
            seen_edges.add(pair)
        return issues
