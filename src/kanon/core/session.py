from __future__ import annotations

import hashlib
from enum import Enum
from typing import Literal

from pydantic import BaseModel, field_validator

from kanon.core.config import KanonConfig
from kanon.core.yaml_utils import dump_yaml, load_yaml

SESSION_FILE = "session.yaml"


# ── models ────────────────────────────────────────────────────────────────────

class FindingType(str, Enum):
    bug = "bug"
    grammar = "grammar"
    kanon = "kanon"
    question = "question"
    dead_code = "dead_code"
    plan = "plan"
    security = "security"
    test = "test"


class FindingSeverity(str, Enum):
    critical = "critical"
    major = "major"
    minor = "minor"
    nit = "nit"


class PlanStep(BaseModel):
    text: str
    done: bool = False

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip() if v else v


class Finding(BaseModel):
    type: FindingType
    severity: FindingSeverity
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
    status: Literal["open", "approved"] = "open"
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
    meta: SessionMeta = SessionMeta()

    @field_validator("goal", mode="before")
    @classmethod
    def strip_goal(cls, v: str) -> str:
        return v.strip() if v else v



# ── persistence ───────────────────────────────────────────────────────────────

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_session() -> tuple[SessionState, str]:
    """Load session.yaml; return (state, file_hash). Raises FileNotFoundError if absent."""
    path = KanonConfig.root() / SESSION_FILE
    text = path.read_text()
    state = load_yaml(path, SessionState)
    return state, _hash(text)

def save_session(state: SessionState) -> tuple[str, str]:
    """Save session.yaml; return (before_hash, after_hash)."""
    path = KanonConfig.root() / SESSION_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = dump_yaml(state)
    path.write_text(text)
    after = _hash(text)
    return before, after


def create_session(goal: str) -> tuple[SessionState, str]:
    """Create session.yaml with goal. Raises FileExistsError if it already exists."""
    path = KanonConfig.root() / SESSION_FILE
    if path.exists():
        raise FileExistsError(f"{SESSION_FILE} already exists. Use 'kanon session clear' first.")
    path.parent.mkdir(parents=True, exist_ok=True)
    state = SessionState(goal=goal)
    text = dump_yaml(state)
    path.write_text(text)
    return state, _hash(text)


def delete_session() -> None:
    """Delete session.yaml. Raises FileNotFoundError if absent."""
    path = KanonConfig.root() / SESSION_FILE
    path.unlink()


# ── key generation ────────────────────────────────────────────────────────────

def _next_key(state: SessionState, namespace: str) -> str:
    n = state.meta.next_key.get(namespace, 1)
    state.meta.next_key[namespace] = n + 1
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
