# kanon-audit

**Date:** 2026-06-06
**Status:** open

## Findings

### F1: Test layout does not mirror source layout
**Kanon:** `python/testing/base`
**Location:** `tests/`
**Status:** open
**Note:** All test files are flat under `tests/` regardless of source depth. `src/kanon/core/config.py` maps to `tests/test_config.py` instead of `tests/core/test_config.py`; `src/kanon/commands/sync/` maps to `tests/test_sync_cli.py` instead of `tests/commands/sync/test_<X>.py`. Applies to all core and commands test files.

### F2: `cli.py` missing `from __future__ import annotations`
**Kanon:** `python/style`
**Location:** `src/kanon/cli.py:1`
**Status:** open
**Note:** The file defines a typed function (`project_root: str`) but lacks the `from __future__ import annotations` import required by the style kanon.
