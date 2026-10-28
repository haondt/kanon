from __future__ import annotations

from kanon.core.table._keys import key_order
from kanon.core.table._models import TableData

_DOTS: dict[str, str] = {"open": "○", "active": "●", "resolved": "✓"}


def status_label(status: str) -> str:
    return f"[{status.center(8)}]"


class TableRenderMixin(TableData):
    def _tally(self) -> str:
        counts = {s: sum(1 for i in self.items.values() if i.status == s) for s in _DOTS}
        total = len(self.items)
        return f"{total} item{'s' if total != 1 else ''}: {counts['active']} active · {counts['open']} open · {counts['resolved']} resolved"

    def render_graph(self) -> str:
        if not self.items:
            return "Table is empty."

        adj = {k: self.neighbors(k) for k in self.items}
        order: dict[str, int] = {}
        parent: dict[str, str] = {}
        children: dict[str, list[str]] = {k: [] for k in self.items}

        def visit(node: str) -> None:
            order[node] = len(order)
            for other in adj[node]:
                if other not in order:
                    parent[other] = node
                    children[node].append(other)
                    visit(other)

        seen: set[str] = set()
        roots: list[str] = []
        for key in sorted(self.items, key=key_order):
            if key in seen:
                continue
            component, stack = [], [key]
            while stack:
                node = stack.pop()
                if node not in seen:
                    seen.add(node)
                    component.append(node)
                    stack.extend(adj[node])
            active = [n for n in component if self.items[n].status == "active"]
            roots.append(active[0] if active else key)
        roots.sort(key=lambda r: (self.items[r].status != "active", key_order(r)))
        for root in roots:
            visit(root)

        extras: dict[str, list[str]] = {k: [] for k in self.items}
        for e in self.edges:
            if parent.get(e.a) == e.b or parent.get(e.b) == e.a:
                continue
            later, earlier = (e.a, e.b) if order[e.a] > order[e.b] else (e.b, e.a)
            extras[later].append(earlier)

        def describe(key: str) -> str:
            item = self.items[key]
            return f"{_DOTS[item.status]} {key}  {item.title}"

        rows: list[tuple[str, str]] = []

        def emit(key: str, prefix: str, connector: str, child_prefix: str) -> None:
            links = ", ".join(sorted(extras[key], key=key_order))
            rows.append((f"{prefix}{connector}{describe(key)}", f"↔ {links}" if links else ""))
            kids = children[key]
            for i, kid in enumerate(kids):
                last = i == len(kids) - 1
                emit(kid, child_prefix, "└─ " if last else "├─ ", child_prefix + ("   " if last else "│  "))

        blocks: list[list[tuple[str, str]]] = []
        for root in roots:
            rows = []
            emit(root, "", "", "")
            blocks.append(rows)

        width = max(len(left) for block in blocks for left, _ in block)
        rendered = [
            "\n".join(f"{left:<{width}}  {right}".rstrip() for left, right in block)
            for block in blocks
        ]
        return self._tally() + "\n\n" + "\n\n".join(rendered)
