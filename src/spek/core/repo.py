from __future__ import annotations

import importlib.resources
from pathlib import Path

import git


def spek_repo_path() -> Path:
    """Return the path to the spek package's own repo root (where specs/ lives)."""
    pkg_path = Path(importlib.resources.files("spek").__str__())
    candidate = pkg_path
    while candidate != candidate.parent:
        if (candidate / ".git").exists():
            return candidate
        candidate = candidate.parent
    raise RuntimeError("Could not locate spek repo root (no .git found)")


def spek_sha(repo_path: Path | None = None) -> str:
    """Return the current HEAD SHA of the spek repo."""
    path = repo_path or spek_repo_path()
    repo = git.Repo(path)
    return repo.head.commit.hexsha
