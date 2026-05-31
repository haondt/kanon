from __future__ import annotations

from typing import Any

from pathlib import Path


def deep_merge(d1: dict[str, Any], d2: dict[str, Any], conflicts: str = "new", _path: str = ""):
    if conflicts not in ["new", "old", "err"]:
        raise ValueError("Unexpected conflict resolution:" + conflicts)
    def merge_list(l1: list[Any], l2: list[Any]):
        l: list[Any] = []
        for v in l1 + l2:
            if v not in l:
                l.append(v)
        return l
    result = d1.copy()
    for k, v in d2.items():
        if k not in result:
            result[k] = v
            continue
        if type(v) != type(result[k]):
            if conflicts == "new":
                result[k] = v
            elif conflicts == "err":
                raise KeyError(f"Multiple entries found for key: {_path}.{k}")
            continue
        if isinstance(v, dict):
            result[k] = deep_merge(result[k], v, conflicts, _path + "." + k) # pyright: ignore[reportUnknownArgumentType]
            continue
        if isinstance(v, (tuple, list)):
            result[k] = merge_list(result[k], v) # pyright: ignore[reportArgumentType]
            continue

        if conflicts == "new":
            result[k] = v
        elif conflicts == "err":
            raise KeyError(f"Multiple entries found for key: {_path}.{k}")
    return result

def resolve_path(path: str | Path | None) -> Path:
    if path == None:
        path = "."
    if isinstance(path, str):
        path = Path(path)
    return path.resolve()
