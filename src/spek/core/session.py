from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, field_validator

SESSION_FILE = ".spek/session.yaml"


# ── YAML representer ──────────────────────────────────────────────────────────

def _literal_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _make_dumper() -> type[yaml.Dumper]:
    class _Dumper(yaml.Dumper):
        pass
    _Dumper.add_representer(str, _literal_representer)
    return _Dumper


# ── models ────────────────────────────────────────────────────────────────────

def _strip(v: str | None) -> str | None:
    return v.strip() if v else v


class PlanStep(BaseModel):
    text: str
    done: bool = False

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip() if v else v


class Finding(BaseModel):
    text: str
    status: Literal["open", "closed", "reopened"] = "open"
    fix_note: str | None = None

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip() if v else v

    @field_validator("fix_note", mode="before")
    @classmethod
    def strip_fix_note(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class ReviewPass(BaseModel):
    findings: dict[str, Finding] = {}


class BuildSection(BaseModel):
    notes: dict[str, str] = {}


class PlanSection(BaseModel):
    steps: dict[str, PlanStep] = {}
    notes: dict[str, str] = {}


class SessionMeta(BaseModel):
    next_key: dict[str, int] = {}


class SessionState(BaseModel):
    goal: str
    plan: PlanSection = PlanSection()
    stance: str | None = None
    build: BuildSection = BuildSection()
    review: dict[str, ReviewPass] = {}
    amendments: list[str] = []
    detours: list[str] = []
    _meta: SessionMeta = SessionMeta()

    @field_validator("goal", mode="before")
    @classmethod
    def strip_goal(cls, v: str) -> str:
        return v.strip() if v else v

    model_config = {"populate_by_name": True}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionState:
        meta_data = data.pop("_meta", {})
        obj = cls.model_validate(data)
        obj._meta = SessionMeta.model_validate(meta_data)
        return obj

    def to_dict(self) -> dict[str, Any]:
        d = self.model_dump(exclude_none=True, exclude_defaults=True, exclude={"_meta"})
        # always include goal and plan
        d["goal"] = self.goal
        if self.plan.steps or self.plan.notes:
            d["plan"] = {}
            if self.plan.steps:
                d["plan"]["steps"] = {k: v.model_dump(exclude_defaults=True) for k, v in self.plan.steps.items()}
            if self.plan.notes:
                d["plan"]["notes"] = dict(self.plan.notes)
        meta_d = self._meta.model_dump(exclude_defaults=True)
        if meta_d:
            d["_meta"] = meta_d
        return d


# ── persistence ───────────────────────────────────────────────────────────────

def _dump(state: SessionState) -> str:
    buf = io.StringIO()
    yaml.dump(state.to_dict(), buf, Dumper=_make_dumper(), default_flow_style=False, sort_keys=False,
              allow_unicode=True)
    return buf.getvalue()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_session(project_root: Path) -> tuple[SessionState, str]:
    """Load session.yaml; return (state, file_hash). Raises FileNotFoundError if absent."""
    path = project_root / SESSION_FILE
    text = path.read_text()
    raw: dict[str, Any] = yaml.safe_load(text) or {}
    state = SessionState.from_dict(raw)
    return state, _hash(text)


def save_session(state: SessionState, project_root: Path) -> tuple[str, str]:
    """Save session.yaml; return (before_hash, after_hash)."""
    path = project_root / SESSION_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = _dump(state)
    path.write_text(text)
    after = _hash(text)
    return before, after


def create_session(goal: str, project_root: Path) -> tuple[SessionState, str]:
    """Create session.yaml with goal. Raises FileExistsError if it already exists."""
    path = project_root / SESSION_FILE
    if path.exists():
        raise FileExistsError(f"{SESSION_FILE} already exists. Use 'spek session clear' first.")
    path.parent.mkdir(parents=True, exist_ok=True)
    state = SessionState(goal=goal)
    text = _dump(state)
    path.write_text(text)
    return state, _hash(text)


def delete_session(project_root: Path) -> None:
    """Delete session.yaml. Raises FileNotFoundError if absent."""
    path = project_root / SESSION_FILE
    path.unlink()


# ── key generation ────────────────────────────────────────────────────────────

def _next_key(state: SessionState, namespace: str) -> str:
    n = state._meta.next_key.get(namespace, 1)
    state._meta.next_key[namespace] = n + 1
    return f"{namespace}{n}"


def next_plan_note_key(state: SessionState) -> str:
    return _next_key(state, "pn")


def next_build_note_key(state: SessionState) -> str:
    return _next_key(state, "bn")


def next_finding_key(state: SessionState) -> str:
    return _next_key(state, "f")


def next_pass_key(state: SessionState) -> str:
    return _next_key(state, "p")


# ── lint ──────────────────────────────────────────────────────────────────────

def lint_session(state: SessionState) -> list[str]:
    issues: list[str] = []
    if not state.goal.strip():
        issues.append("goal is empty")
    return issues
