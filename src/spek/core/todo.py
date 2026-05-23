from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, field_validator

from spek.core.session import _literal_representer, _make_dumper

TODO_FILE = ".spek/todo.yaml"


# ── models ────────────────────────────────────────────────────────────────────

class TodoSection(BaseModel):
    name: str
    items: list[str] = []

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if v else v

    @field_validator("items", mode="before")
    @classmethod
    def strip_items(cls, v: list[str]) -> list[str]:
        return [i.strip() for i in v] if v else v


class TodoState(BaseModel):
    sections: dict[str, TodoSection] = {}


# ── persistence ───────────────────────────────────────────────────────────────

def _dump(state: TodoState) -> str:
    d = state.model_dump(exclude_defaults=True)
    buf = io.StringIO()
    yaml.dump(d, buf, Dumper=_make_dumper(), default_flow_style=False, sort_keys=False, allow_unicode=True)
    return buf.getvalue()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_todo(project_root: Path) -> tuple[TodoState, str]:
    """Load todo.yaml; return (state, file_hash). Raises FileNotFoundError if absent."""
    path = project_root / TODO_FILE
    text = path.read_text()
    raw: dict[str, Any] = yaml.safe_load(text) or {}
    state = TodoState.model_validate(raw)
    return state, _hash(text)


def save_todo(state: TodoState, project_root: Path) -> tuple[str, str]:
    """Save todo.yaml; return (before_hash, after_hash)."""
    path = project_root / TODO_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = _dump(state)
    path.write_text(text)
    after = _hash(text)
    return before, after


def create_todo(project_root: Path) -> tuple[TodoState, str]:
    """Create an empty todo.yaml. Raises FileExistsError if it already exists."""
    path = project_root / TODO_FILE
    if path.exists():
        raise FileExistsError(f"{TODO_FILE} already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    state = TodoState()
    text = _dump(state)
    path.write_text(text)
    return state, _hash(text)


# ── lint ──────────────────────────────────────────────────────────────────────

def lint_todo(state: TodoState) -> list[str]:
    issues: list[str] = []
    for key, section in state.sections.items():
        if not section.name.strip():
            issues.append(f"section {key!r} has empty name")
        for item in section.items:
            if not item.strip():
                issues.append(f"section {key!r} has empty item")
    return issues
