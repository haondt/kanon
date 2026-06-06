# kanon-audit

**Date:** 2026-06-06
**Status:** open

## Findings

### F1: Relative imports in commands/session/ and commands/todo/
**Kanon:** `haondt::python/style`
**Location:** `src/kanon/commands/session/__init__.py:5-11`, `src/kanon/commands/session/amend.py:7`, `src/kanon/commands/session/build.py:8`, `src/kanon/commands/session/commands.py:13`, `src/kanon/commands/session/detour.py:7`, `src/kanon/commands/session/plan.py:6`, `src/kanon/commands/session/review.py:8`, `src/kanon/commands/session/stance.py:7`, `src/kanon/commands/todo/__init__.py:5-6`, `src/kanon/commands/todo/commands.py:9,85,102`, `src/kanon/commands/todo/section.py:8`
**Status:** open
**Note:** All use `from ._helpers import ...` or `from .commands import ...` rather than absolute imports. Two occurrences in `todo/commands.py` are also inside function bodies (lines 85, 102), which is non-standard.

### F2: config.py at 429 lines with separable concerns
**Kanon:** `haondt::python/style`
**Location:** `src/kanon/core/config.py`
**Status:** open
**Note:** File is 429 lines. Contains two clearly separable clusters: (1) environment/project config — `KanonEnv`, `KanonMeta`, `KanonConfig`, integration enums, output-dir/settings constants; (2) reference parsing — `SourceReference`, `SourcedResource`, and their associated constants and helpers. The kanon says to split at natural seams above 200 lines.

### F3: cli.py missing `from __future__ import annotations`
**Kanon:** `haondt::python/style`
**Location:** `src/kanon/cli.py`
**Status:** open
**Note:** File has a type annotation (`project_root: str`) but lacks the `from __future__ import annotations` import required by the style kanon. All other non-trivial Python source files include it.
