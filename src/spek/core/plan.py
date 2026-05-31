from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from spek.core.session import PlanStep
from spek.core.yaml_utils import _make_dumper

PLANS_DIR = ".spek/plans"


# ── models ────────────────────────────────────────────────────────────────────

class PlanMeta(BaseModel):
    next_key: dict[str, int] = {}


class PlanFile(BaseModel):
    goal: str
    steps: dict[str, PlanStep] = {}
    notes: dict[str, str] = {}
    _meta: PlanMeta = PlanMeta()

    model_config = {"populate_by_name": True}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlanFile:
        meta_data = data.pop("_meta", {})
        obj = cls.model_validate(data)
        obj._meta = PlanMeta.model_validate(meta_data)
        return obj

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"goal": self.goal}
        if self.steps:
            d["steps"] = {k: v.model_dump(exclude_defaults=True) for k, v in self.steps.items()}
        if self.notes:
            d["notes"] = dict(self.notes)
        meta_d = self._meta.model_dump(exclude_defaults=True)
        if meta_d:
            d["_meta"] = meta_d
        return d


class SplitEntry(BaseModel):
    status: Literal["pending", "in_progress", "done"] = "pending"


class SplitIndex(BaseModel):
    goal: str
    plans: dict[str, SplitEntry] = {}

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"goal": self.goal}
        if self.plans:
            d["plans"] = {k: v.model_dump(exclude_defaults=True) for k, v in self.plans.items()}
        return d


# ── path helpers ──────────────────────────────────────────────────────────────

def parse_plan_ref(name: str) -> tuple[str | None, str]:
    """Parse a plan name into (split, plan_name). Errors on >1 slash."""
    parts = name.split("/")
    if len(parts) == 1:
        return None, parts[0]
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(f"Plan name {name!r} must be bare '<name>' or '<split>/<name>'")


def plan_path(root: Path, name: str) -> Path:
    """Return the path for a plan file given its name (bare or split/name)."""
    split, plan_name = parse_plan_ref(name)
    if split is None:
        return root / PLANS_DIR / f"{plan_name}.yaml"
    return root / PLANS_DIR / split / f"{plan_name}.yaml"


def index_path(root: Path, split: str) -> Path:
    """Return the path for a split's index.yaml."""
    return root / PLANS_DIR / split / "index.yaml"


# ── persistence ───────────────────────────────────────────────────────────────

def _dump_plan(plan: PlanFile) -> str:
    buf = io.StringIO()
    yaml.dump(plan.to_dict(), buf, Dumper=_make_dumper(), default_flow_style=False, sort_keys=False, allow_unicode=True)
    return buf.getvalue()


def _dump_index(index: SplitIndex) -> str:
    buf = io.StringIO()
    yaml.dump(index.to_dict(), buf, Dumper=_make_dumper(), default_flow_style=False, sort_keys=False, allow_unicode=True)
    return buf.getvalue()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_plan(root: Path, name: str) -> tuple[PlanFile, str]:
    """Load a plan file. Returns (plan, hash). Raises FileNotFoundError if absent."""
    path = plan_path(root, name)
    text = path.read_text()
    raw: dict[str, Any] = yaml.safe_load(text) or {}
    return PlanFile.from_dict(raw), _hash(text)


def save_plan(plan: PlanFile, root: Path, name: str) -> tuple[str, str]:
    """Save a plan file. Returns (before_hash, after_hash)."""
    path = plan_path(root, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = _dump_plan(plan)
    path.write_text(text)
    return before, _hash(text)


def create_plan(goal: str, root: Path, name: str) -> tuple[PlanFile, str]:
    """Create a new plan file. Raises FileExistsError if it already exists."""
    path = plan_path(root, name)
    if path.exists():
        raise FileExistsError(f"Plan {name!r} already exists at {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    plan = PlanFile(goal=goal)
    text = _dump_plan(plan)
    path.write_text(text)
    return plan, _hash(text)


def load_split_index(root: Path, split: str) -> tuple[SplitIndex, str]:
    """Load a split index.yaml. Returns (index, hash). Raises FileNotFoundError if absent."""
    path = index_path(root, split)
    text = path.read_text()
    raw: dict[str, Any] = yaml.safe_load(text) or {}
    return SplitIndex.model_validate(raw), _hash(text)


def save_split_index(index: SplitIndex, root: Path, split: str) -> tuple[str, str]:
    """Save a split index. Returns (before_hash, after_hash)."""
    path = index_path(root, split)
    path.parent.mkdir(parents=True, exist_ok=True)
    before_text = path.read_text() if path.exists() else ""
    before = _hash(before_text)
    text = _dump_index(index)
    path.write_text(text)
    return before, _hash(text)


def create_split(goal: str, root: Path, split: str) -> tuple[SplitIndex, str]:
    """Create a new split index. Raises FileExistsError if it already exists."""
    path = index_path(root, split)
    if path.exists():
        raise FileExistsError(f"Split {split!r} already exists at {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    index = SplitIndex(goal=goal)
    text = _dump_index(index)
    path.write_text(text)
    return index, _hash(text)


# ── key generation ────────────────────────────────────────────────────────────

def next_note_key(plan: PlanFile) -> str:
    n = plan._meta.next_key.get("pn", 1)
    plan._meta.next_key["pn"] = n + 1
    return f"pn{n}"
