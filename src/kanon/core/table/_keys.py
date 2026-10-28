from __future__ import annotations


def key_for(index: int) -> str:
    """Spreadsheet-style key: 0 → a, 25 → z, 26 → aa."""
    n = index + 1
    key = ""
    while n:
        n, rem = divmod(n - 1, 26)
        key = chr(97 + rem) + key
    return key


def key_order(key: str) -> tuple[int, str]:
    return len(key), key


def edge_pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if key_order(a) <= key_order(b) else (b, a)
