from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kanon.core.ledger._data import Progress
from kanon.core.ledger._models import ListItemEntry, ScalarEntry, JsonEntry
from kanon.core.ledger._persistence import LedgerPersistenceMixin
from kanon.core.ledger._target import TargetFileError, backup_target
from kanon.core.yaml_utils import save_json


class JsonFileError(TargetFileError):
    pass


def load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON object; a missing file is an empty object."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise JsonFileError(f"{path} is not valid JSON (comments are not supported): {e}") from e


def check_json_file_readable(path: Path) -> None:
    """Raise JsonFileError if `path` exists but cannot be parsed."""
    load_json_file(path)


def save_json_file(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    save_json(data, path)


_MISSING = object()


def _merge(
    current: dict[str, Any],
    desired: dict[str, Any],
    path: list[str],
    entries: list[JsonEntry],
) -> None:
    for key, value in desired.items():
        here = [*path, key]
        if isinstance(value, dict):
            child = current.setdefault(key, {})
            _merge(child, value, here, entries)  # pyright: ignore[reportUnknownArgumentType]
        elif isinstance(value, list):
            existing = current.setdefault(key, [])
            for item in value:
                if item not in existing:
                    existing.append(item)
                    entries.append(ListItemEntry(path=here, value=item))
        else:
            prior = current.get(key, _MISSING)
            current[key] = value
            entries.append(ScalarEntry(path=here, had_prior=prior is not _MISSING, prior=None if prior is _MISSING else prior, written=value))


def _describe(entry: JsonEntry) -> str:
    dotted = ".".join(entry.path)
    if isinstance(entry, ListItemEntry):
        return f"{dotted} + {json.dumps(entry.value)}"
    return f"{dotted} = {json.dumps(entry.written)}"


def _get_parent(data: dict[str, Any], path: list[str]) -> dict[str, Any] | None:
    node: Any = data
    for key in path[:-1]:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node if isinstance(node, dict) else None  # pyright: ignore[reportUnknownVariableType]


class LedgerJsonMixin(LedgerPersistenceMixin):
    def apply_json(
        self,
        integration: str,
        target: Path,
        desired: dict[str, Any],
        on_progress: Progress = None,
    ) -> None:
        """Merge `desired` into the JSON file at `target`, recording what was added so it can be rewound."""
        backup_target(target)

        data = load_json_file(target)
        entries: list[JsonEntry] = []
        _merge(data, desired, [], entries)
        save_json_file(data, target)

        recorded = self.integration_ledger(integration).json_files.setdefault(str(target), [])
        for entry in entries:
            recorded.append(entry)
            if on_progress:
                on_progress(f"  ledger: {integration} {target} {_describe(entry)}")
        self.save()

    def rewind_json(
        self,
        integration: str,
        target: Path,
        on_progress: Progress = None,
    ) -> None:
        """Undo everything `apply_json` recorded for `integration` in `target`."""
        recorded = self.integrations.get(integration)
        entries = recorded.json_files.pop(str(target), []) if recorded else []
        self.prune(integration)
        if not entries:
            self.save()
            return

        data = load_json_file(target)
        for entry in reversed(entries):
            parent = _get_parent(data, entry.path)
            key = entry.path[-1]
            if parent is None or key not in parent:
                continue
            if isinstance(entry, ListItemEntry):
                if isinstance(parent[key], list) and entry.value in parent[key]:
                    parent[key].remove(entry.value)
                    if on_progress:
                        on_progress(f"  ledger: {integration} {target} rewound {_describe(entry)}")
                continue
            if parent[key] != entry.written:
                if on_progress:
                    on_progress(
                        f"  warning: {'.'.join(entry.path)} in {target} was changed since kanon wrote it; leaving it as is"
                    )
                continue
            if entry.had_prior:
                parent[key] = entry.prior
            else:
                del parent[key]
            if on_progress:
                on_progress(f"  ledger: {integration} {target} rewound {_describe(entry)}")
        save_json_file(data, target)
        self.save()
