from __future__ import annotations

import hashlib

from pydantic import BaseModel, Field, field_validator

from kanon.core.config import KanonConfig
from kanon.core.yaml_utils import dump_yaml, parse_yaml

TODO_FILE = "todo.yaml"


# ── models ────────────────────────────────────────────────────────────────────

class TodoSection(BaseModel):
    name: str
    items: list[str] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if v else v

    @field_validator("items", mode="before")
    @classmethod
    def strip_items(cls, v: list[str]) -> list[str]:
        return [i.strip() for i in v] if v else v


class TodoState(BaseModel):
    sections: dict[str, TodoSection] = Field(default_factory=dict)


# ── persistence ───────────────────────────────────────────────────────────────

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_todo() -> tuple[TodoState, str]:
    """Load todo.yaml; return (state, file_hash). Raises FileNotFoundError if absent."""
    path = KanonConfig.root() / TODO_FILE
    text = path.read_text()
    state = TodoState.model_validate(parse_yaml(text))
    return state, _hash(text)


def save_todo(state: TodoState) -> tuple[str, str]:
    """Save todo.yaml; return (before_hash, after_hash)."""
    path = KanonConfig.root() / TODO_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = dump_yaml(state)
    path.write_text(text)
    after = _hash(text)
    return before, after


def create_todo() -> tuple[TodoState, str]:
    """Create an empty todo.yaml. Raises FileExistsError if it already exists."""
    path = KanonConfig.root() / TODO_FILE
    if path.exists():
        raise FileExistsError(f"{TODO_FILE} already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    state = TodoState()
    text = dump_yaml(state)
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
