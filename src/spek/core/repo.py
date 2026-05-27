from __future__ import annotations

from pathlib import Path


def local_project_path() -> Path | None:
    """Return the root of the local spek project (containing .spek/spek.yaml), or None."""
    candidate = Path.cwd()
    while candidate != candidate.parent:
        if (candidate / ".spek" / "spek.yaml").exists():
            return candidate
        candidate = candidate.parent
    return None
